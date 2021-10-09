import pandas as pd
import requests
import base64
import json

class airtableDataMapper(object):
    def __init__(self, baseKey, APIkey):
        self.baseKey = baseKey
        self.APIkey = APIkey
        self.headers = {"Content-type":"text/plain","Authorization":f"Bearer {self.APIkey}"}
        
        # Inital data pull via Airtable API
        def getTableJSON(tableName):
            requestStr = f'https://api.airtable.com/v0/{self.baseKey}/{tableName.replace(" ","%20")}'
            api_response = requests.get(requestStr, headers=self.headers)
            response_json = json.loads(api_response.text)
            return response_json
        self.outputFormats = getTableJSON("Output Formats")
        self.dataSources = getTableJSON("Data Sources")

        #DICTIONARIES
        # - - - - - - - - - - - - - -
        # table's row Names to ID
        self.outputNameToID = { x['fields']['OutputID'] : x['id'] for x in self.outputFormats['records'] }
        # table's row ID to Names
        self.sourceIDToName = { x['id'] : x['fields']['SourceName'] for x in self.dataSources['records'] }
        # - - - - - - - - - - - - - -

    # pulls mapping information associated with a specific view and preps mapping objects
    def findMappingView(self,viewName):
        self.viewName = viewName
        self.targetOutputID = self.outputNameToID[self.viewName]
        
        # Remainder of data pulled when an output view name is provided
        def getTableViewJSON(tableName):
            requestStr = f'https://api.airtable.com/v0/{self.baseKey}/{tableName.replace(" ","%20")}?view={self.viewName.replace(" ","%20")}'
            api_response = requests.get(requestStr, headers=self.headers)
            response_json = json.loads(api_response.text)
            return response_json
        self.dataMap = getTableViewJSON("Data Map Demo")
        self.dataConnectors =  getTableViewJSON("Merge Connectors")

        # lists of all input and output sourceIDs and names
        self.inputSourceIDs = list({ x['fields']['InputSource'][0] for x in self.dataMap['records'] if self.targetOutputID in x['fields']['OutputFormat'] })
        self.inputSourceNames = [*map(self.sourceIDToName.get, self.inputSourceIDs)]
        self.outputSourceIDs = list({ x['fields']['OutputSource'][0] for x in self.dataMap['records'] if self.targetOutputID in x['fields']['OutputFormat'] })
        self.outputSourceNames = [*map(self.sourceIDToName.get, self.outputSourceIDs)]
            
        # Compiles all input/output sources, and queries for mapped columns.
        # Minimizes data pulled by filtering for only sources used in the mapping.
        tempAllSourceNames = self.inputSourceNames.copy()
        tempAllSourceNames.extend(self.outputSourceNames.copy())
        chainedSourcesAPI_str = ",".join([f"DataSource='{x}'" for x in tempAllSourceNames])
        filterFormula_str = f"OR({chainedSourcesAPI_str})"
        queryStr = {"filterByFormula":filterFormula_str}
        requestStr = f'https://api.airtable.com/v0/{self.baseKey}/{"Data Columns".replace(" ","%20")}'
        api_response = requests.get(requestStr, headers=self.headers, params=queryStr)
        self.dataColumns = json.loads(api_response.text)

        #DICTIONARIES
        # - - - - - - - - - - - - - -
        # table's ID to other table's ID
        self.columnIDToSourceID = { x['id'] : x['fields']['DataSource'][0] for x in self.dataColumns['records'] }
        # table's row ID to Names
        self.columnIDToName = { x['id'] : x['fields']['ColumnName'] for x in self.dataColumns['records'] }
        # - - - - - - - - - - - - - -

        #LISTS
        # - - - - - - - - - - - - - -       
        #nested list of merge column ID pairs
        self.mergeColIDPairs = [x['fields']['MergeColumns'] for x in self.dataConnectors['records']]
        #flat list of all merge column IDs
        self.mergeColIDsList = [i for sub in self.mergeColIDPairs for i in sub]
        #identifies input sources
        self.inputColsInOutput = [ x['fields']['InputColumn'][0] for x in self.dataMap['records'] if (self.targetOutputID in x['fields']['OutputFormat']) and (x['fields']['InputColumn'][0] in self.mergeColIDsList) ]
        # - - - - - - - - - - - - - -    
 
        # preparations for data mapping 
        map_df = pd.json_normalize(self.dataMap['records'])
        map_col_rename_dict = {x : x.replace("fields.","") for x in map_df.columns.tolist()}
        map_df = map_df.rename(columns=map_col_rename_dict)
        list_cols = ['OutputFormat','InputColumn','OutputColumn','MaxLength','ColumnPosition','DataType','Format','Active','Description','Required']
        map_df[list_cols] = map_df[list_cols].apply(lambda x: x.str[0])
        map_df = map_df[map_df['OutputFormat']==self.targetOutputID].reset_index(drop=True)
        map_df['InputSource'] = map_df.loc[:,'InputColumn'].copy().map(self.columnIDToSourceID).map(self.sourceIDToName)
        map_df['InputColumn'] = map_df['InputColumn'].map(self.columnIDToName)
        map_df['OutputColumn'] = map_df['OutputColumn'].map(self.columnIDToName)
        map_df = map_df[['OutputColumn','InputColumn','InputSource','MaxLength','ColumnPosition','DataType','Format','Active','Description','Required']]
        map_df = map_df.sort_values(by='InputSource').reset_index(drop=True)
        self.map_df = map_df.sort_values(by='ColumnPosition')  
        return self
    
    def inputSources(self):
        return self.inputSourceNames 

    def inputColumns(self):
        inputCols_df = self.map_df[['InputSource','InputColumn','OutputColumn']].copy()
        return inputCols_df

    def mapData(self,data):
        #creates inital source to column dictionary used to pull all column from a source during merging
        temp_df = self.map_df[['InputColumn','InputSource']].copy()
        sourceColNames = { x : temp_df[temp_df['InputSource']==x]['InputColumn'].tolist() 
                          for x in temp_df['InputSource'].tolist() }
        
        # Creates a list of column IDs that arent in output columns that must be captured for merging
        mergeColsToAppend = [ i for sub in self.mergeColIDPairs for i in sub 
                             for x in self.inputColsInOutput if i != x ]
        # Adds source to each mergeColsToAppend column as nested list pairs.
        mergeSourceColsToAppend = [ [self.sourceIDToName[self.columnIDToSourceID[x]],
                                     self.columnIDToName[x]] for x in mergeColsToAppend ]
        #Adds each mergeSourceColsToAppend pair to the sourceColNames dictionary.
        #ensures we have captured all ouput columns and any column we need for merging datasets.                          
        for scPair in mergeSourceColsToAppend:
            sourceColNames[scPair[0]].append(scPair[1])

        # Creates data for merge columns for column translation (for merge) and actual merge logic
        merge_data = [ {'SourceToRename':self.columnIDToSourceID[i], 'Key':i, 'Value':x,
                        'MergeSources':[self.columnIDToSourceID[i],self.columnIDToSourceID[x]]} 
                      for sub in self.mergeColIDPairs for i in sub 
                      for x in self.inputColsInOutput if i != x ]
        merge_df = pd.DataFrame(data=merge_data)
        merge_df['Key'] = merge_df['Key'].map(self.columnIDToName)
        merge_df['Value'] = merge_df['Value'].map(self.columnIDToName)
        merge_df['SourceToRename'] = merge_df['SourceToRename'].map(self.sourceIDToName)
        merge_df['MergeSources'] = merge_df['MergeSources'].apply(lambda x : [*map(self.sourceIDToName.get, x)])
        merge_df['KeyValuePair'] = [{key:value} for key,value in zip(merge_df['Key'],merge_df['Value'])]

        #creates dict used to convert a sources merge column to the correct merge column name
        temp_df = merge_df[['SourceToRename','KeyValuePair']].copy().set_index('SourceToRename')
        mergeColConvert = temp_df.to_dict()['KeyValuePair']

        #reduces data dfs to only the columns we want and converts merge columns to a unified column merge name
        for source in sourceColNames:
            data[source] = data[source][sourceColNames[source]]
            if source in mergeColConvert:
                data[source] = data[source].rename(columns=mergeColConvert[source])

        #creates a nested list of merge column and its sources, used to orchestrate dataset merging
        temp_df = merge_df[['Value','MergeSources']].copy()
        mergeColAndSources = temp_df.values.tolist()
        
        #initial all_data_df setup using first merge
        all_data_df = data[mergeColAndSources[0][1][0]].merge(data[mergeColAndSources[0][1][1]], on=mergeColAndSources[0][0])
        mergedSourcesCheck = [mergeColAndSources[0][1][0], mergeColAndSources[0][1][1]]
        mergeColAndSources.remove(mergeColAndSources[0])

        #merge all other data sets together
        for merger in mergeColAndSources:
            if merger[1][0] in mergedSourcesCheck and merger[1][1] in mergedSourcesCheck:
                pass
            elif merger[1][0] in mergedSourcesCheck:
                all_data_df = all_data_df.merge(data[merger[1][1]],how='left',on=merger[0])
                mergedSourcesCheck.append(merger[1][1])
            elif merger[1][1] in mergedSourcesCheck:
                all_data_df = all_data_df.merge(data[merger[1][0]],how='left',on=merger[0])
                mergedSourcesCheck.append(merger[1][0])

        # creates dictionary of input columns to output columns
        # used to convert all_data_df input columns to the corresponding output column name
        temp_df = self.map_df[['InputColumn','OutputColumn']].set_index('InputColumn')
        inputColsToOutput = temp_df.to_dict()['OutputColumn']

        all_data_df = all_data_df.rename(columns=inputColsToOutput)
        
        return all_data_df