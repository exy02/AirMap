<a href="https://airtable.com/">
    <img src="https://github.com/eyan02/AirMap/blob/main/images/airtable-icon.svg" alt="Airtable logo" title="AirMap" align="right" height="80" />
</a>

# AirMap
<!-- ## Table of Contents
* [Examples](#examples) -->

AirMap is a data mapper powered by Airtable. Easily keep track of data dictionaries, mappings, sources, columns, and validations.
<br></br>

## Benefits
* Update master data mappings in Airtable, AirMap will automatically update your pipelines to match what you have in the cloud!
* Airtable centralizes all of your data's information, everything you need in one place.
* No need to send static documents back and forth, easily collaborate with others via Airtable's easy-to-use web/desktop GUIs.
* Quickly manage, control, and share your data mappings, validations, and data dictionaries.
<br></br>

<p align="center">Check out the Airtable base <a href="https://airtable.com/shr9Tr2wp5rs2Bm7a">here</a> to get an idea of how the data information is organized. 
</p>
<div width= 100% align="center">
<a href="https://airtable.com/shr9Tr2wp5rs2Bm7a" align="center">
    <img src="https://github.com/eyan02/AirMap/blob/main/images/airtable%20base%20embed.png" alt="Airtable embed" width="450px" />
</a>
</div>
<br></br>

    
## Examples:
 
### Map data using a data-map from Airtable 
### (e.g. 'Project A - Client Summary', [view the base here](https://airtable.com/shr9Tr2wp5rs2Bm7a))
#### Demo Input Data Sources
<table>
  <tr>  <td>Internal_Import_Format2</td>  <td>Internal_Table_Format1</td>  <td>Internal_Import_Format1</td>  </tr>
  <tr><td>
    <table border="1" fontsize = "1pt">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>ServicerID</th>
          <th>DocumentID</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>1938472929</td>
          <td>AJ3fLN32jS1SK2</td>
        </tr>
        <tr>
          <th>1</th>
          <td>1293018083</td>
          <td>J2sjldw3nSk4S2l</td>
        </tr>
        <tr>
          <th>2</th>
          <td>9420410832</td>
          <td>2Pn28dh1lsdD0Q</td>
        </tr>
      </tbody>
    </table>
    </td>
    <td>
    <table border="1">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>ServiceLineID</th>
          <th>ProviderID</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>20394822</td>
          <td>1938472929</td>
        </tr>
        <tr>
          <th>1</th>
          <td>20428284</td>
          <td>1293018083</td>
        </tr>
        <tr>
          <th>2</th>
          <td>19428292</td>
          <td>9420410832</td>
        </tr>
      </tbody>
    </table>
    </td>
    <td>
      <table border="1" >
        <thead>
          <tr style="text-align: right;">
            <th></th>
            <th>ServiceDate</th>
            <th>ClientDOB</th>
            <th>PurchaseAmount</th>
            <th>ProviderID</th>
            <th>PurchaseCount</th>
            <th>ClientReview</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>0</th>
            <td>10/09/2021</td>
            <td>7/4/1776</td>
            <td>$103.20</td>
            <td>1938472929</td>
            <td>4</td>
            <td>4.5</td>
          </tr>
          <tr>
            <th>1</th>
            <td>10/07/2021</td>
            <td>12/30/1899</td>
            <td>$120.12</td>
            <td>1293018083</td>
            <td>5</td>
            <td>4.1</td>
          </tr>
          <tr>
            <th>2</th>
            <td>10/08/2021</td>
            <td>1/26/1980</td>
            <td>$84.23</td>
            <td>9420410832</td>
            <td>2</td>
            <td>3.7</td>
          </tr>
        </tbody>
      </table>
    </td></tr></table>
 
 
```python
# Pass the data sources to AirMap and specify the output format you want to create.
# AirMap will automatically organize and map the data sources into your output format designed in Airtable.

Internal_Import_Format1 = pd.read_csv("Internal_Import_Format1.csv",dtype=str)
Internal_Import_Format2 = pd.read_csv("Internal_Import_Format2.csv",dtype=str)
Internal_Table_Format1 = pd.read_csv("Internal_Table_Format1.csv",dtype=str)

data = {'Internal_Import_Format1' : Internal_Import_Format1,
        'Internal_Import_Format2' : Internal_Import_Format2,
        'Internal_Table_Format1' : Internal_Table_Format1 }

airMap = airtableDataMapper(base_key,airAPI_key)
airMap.findMappingView("Project A - Client Summary").mapData(data)
```
#### Resulting output table
<div>
<table border="1">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Line Service ID</th>
      <th>ServiceProviderID</th>
      <th>Date of Service</th>
      <th>PurchaserDOB</th>
      <th>PurchaseAmount</th>
      <th>Document</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20394822</td>
      <td>1938472929</td>
      <td>10/09/2021</td>
      <td>7/4/1776</td>
      <td>$103.20</td>
      <td>AJ3fLN32jS1SK2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20428284</td>
      <td>1293018083</td>
      <td>10/07/2021</td>
      <td>12/30/1899</td>
      <td>$120.12</td>
      <td>J2sjldw3nSk4S2l</td>
    </tr>
    <tr>
      <th>2</th>
      <td>19428292</td>
      <td>9420410832</td>
      <td>10/08/2021</td>
      <td>1/26/1980</td>
      <td>$84.23</td>
      <td>2Pn28dh1lsdD0Q</td>
    </tr>
  </tbody>
</table>
</div>
<br></br>

### You can use AirMap to check a mapping's requirements directly in Python:
```python
# Check input data sources used for a chosen mapping
airMap.findMappingView("Project A - Client Summary").viewInputSources()
```
<div>
  ['Internal_Import_Format2',
 'Internal_Table_Format1',
 'Internal_Import_Format1']
</div>  
<br></br>

```python
# View input data sources used for a chosen mapping
airMap.findMappingView("Project A - Client Summary").viewInputColumns()
```
<table border="1">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>InputSource</th>
      <th>InputColumn</th>
      <th>OutputColumn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Internal_Import_Format1</td>
      <td>ServiceDate</td>
      <td>Date of Service</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Internal_Import_Format1</td>
      <td>ClientDOB</td>
      <td>PurchaserDOB</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Internal_Import_Format1</td>
      <td>ProviderID</td>
      <td>ServiceProviderID</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Internal_Import_Format1</td>
      <td>PurchaseAmount</td>
      <td>PurchaseAmount</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Internal_Table_Format1</td>
      <td>ServiceLineID</td>
      <td>Line Service ID</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Internal_Import_Format2</td>
      <td>DocumentID</td>
      <td>Document</td>
    </tr>
  </tbody>
</table>
<br></br>

```python
# View all mapping details for a chosen mapping
airMap.findMappingView("Project A - Client Summary").viewMap()
```
<table border="1">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>OutputColumn</th>
      <th>InputColumn</th>
      <th>InputSource</th>
      <th>MaxLength</th>
      <th>ColumnPosition</th>
      <th>DataType</th>
      <th>Format</th>
      <th>Active</th>
      <th>Description</th>
      <th>Required</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Date of Service</td>
      <td>ServiceDate</td>
      <td>Internal_Import_Format1</td>
      <td>10</td>
      <td>1</td>
      <td>Date</td>
      <td>mm-dd-yyyy</td>
      <td>Yes</td>
      <td>Date of services rendered</td>
      <td>Y</td>
    </tr>
    <tr>
      <th>1</th>
      <td>PurchaserDOB</td>
      <td>ClientDOB</td>
      <td>Internal_Import_Format1</td>
      <td>10</td>
      <td>2</td>
      <td>Date</td>
      <td>mm-dd-yyyy</td>
      <td>Yes</td>
      <td>Client's date of birth</td>
      <td>Y</td>
    </tr>
    <tr>
      <th>2</th>
      <td>ServiceProviderID</td>
      <td>ProviderID</td>
      <td>Internal_Import_Format1</td>
      <td>10</td>
      <td>3</td>
      <td>String</td>
      <td>##########</td>
      <td>Yes</td>
      <td>Service providers ID</td>
      <td>Y</td>
    </tr>
    <tr>
      <th>3</th>
      <td>PurchaseAmount</td>
      <td>PurchaseAmount</td>
      <td>Internal_Import_Format1</td>
      <td>20</td>
      <td>4</td>
      <td>String</td>
      <td>$dd.cc</td>
      <td>Yes</td>
      <td>Client's purchase</td>
      <td>Y</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Line Service ID</td>
      <td>ServiceLineID</td>
      <td>Internal_Table_Format1</td>
      <td>8</td>
      <td>5</td>
      <td>String</td>
      <td>########</td>
      <td>Yes</td>
      <td>Service providers ID</td>
      <td>Y</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Document</td>
      <td>DocumentID</td>
      <td>Internal_Import_Format2</td>
      <td>10</td>
      <td>6</td>
      <td>String</td>
      <td>NaN</td>
      <td>Yes</td>
      <td>DocumentID</td>
      <td>N</td>
    </tr>
  </tbody>
</table>
