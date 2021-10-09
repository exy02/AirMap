class AirtableAPI(object):
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
        self.dataConnectors =  getTableViewJSON("Merge Connector")

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

        return self
    