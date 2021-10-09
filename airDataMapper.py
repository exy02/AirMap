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
