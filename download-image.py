#!/usr/bin/env python
# coding: utf-8

# ## Importing Modules
# Beberapa module ini digunakan untuk menjalankan code citra downloader dari web http://mounts-project.com

# In[ ]:


import requests
import pandas as pd
import os
from urllib.parse import urljoin
import asyncio
import aiohttp


# ## Setting up variables
# Beberapa variable yang digunakan dan bisa dirubah sesuai dengan kebutuhan

# In[ ]:


STATIC_URL: str = 'http://mounts-project.com/static/'


# In[ ]:


output_directory = os.path.join(os.getcwd(), 'output')
image_output_directory = os.path.join(os.getcwd(), 'image')
thermal_image_directory = os.path.join(image_output_directory, 'thermal')
so2_image_directory = os.path.join(image_output_directory, 'so2')


# ## Checking existsing directory

# In[ ]:


if (not os.path.exists(image_output_directory)):
    os.mkdir(image_output_directory)
    
if (not os.path.exists(thermal_image_directory)):
    os.mkdir(thermal_image_directory)
    
if (not os.path.exists(so2_image_directory)):
    os.mkdir(so2_image_directory)


# ## Read output.csv from previous extraction

# In[ ]:


df_files = pd.read_csv('output.csv')


# In[ ]:


df_files


# In[ ]:


dataframes = {}


# In[ ]:


for index in df_files.index:
    code = df_files['code'][index]
    volcano_name = df_files['volcano_name'][index]
    filename = df_files['filename'][index]
    latest_update = df_files['updated_at'][index]
    
    excel = os.path.join(output_directory, filename)
    
    dataframes[code] = {}
    
    dataframes[code]['volcano_name'] = volcano_name
    dataframes[code]['df'] = pd.read_excel(excel, parse_dates=True, index_col=0)
    dataframes[code]['latest_update'] = latest_update


# In[ ]:


dataframes.keys()


# In[ ]:


if os.path.isfile('latest.csv'):
    latest_df = pd.read_csv('latest.csv', index_col="code")
    print('File latest.csv exists!')
else:
    latest_df = pd.DataFrame()
    print('File latest.csv NOT exists!')


# In[ ]:


latest = []

for code in dataframes.keys():
    volcano_name = dataframes[code]['volcano_name']
    
    # Deciding to download all of the images or download only the latest images
    print('=========================================')
    if latest_df.empty:
        df = dataframes[code]['df']
        print('{}_{}_{}'.format(code, volcano_name, 'all'))
    else:
        latest_download = latest_df['latest_update'][code]
        temp = dataframes[code]['df']
        df = temp.loc[temp.index > latest_download]
        print('{}_{}_{}'.format(code, volcano_name, latest_download))
    print('=========================================')
    
    # Used to update the latest.csv
    latest_update = dataframes[code]['latest_update']
        
    if not df.empty:
        async with aiohttp.ClientSession() as session:
            for index in df.index:
                sub_image_directory = df['Type'][index].lower()
                download_dir = os.path.join(image_output_directory, sub_image_directory, volcano_name)
                os.makedirs(download_dir, exist_ok=True)

                image_path_url = df['Graph'][index]
                url = urljoin(STATIC_URL, image_path_url)
                downloaded_filename = url.split("/")[-1]
                full_path_downloaded_filename = os.path.join(download_dir, downloaded_filename)
                
                # Download if file is not exists
                if not os.path.isfile(full_path_downloaded_filename):
                    async with session.get(url) as response:
                        image = await response.read()

                        if response.ok:
                            with open(full_path_downloaded_filename, 'wb') as f:
                                f.write(image)
                                print('Image sucessfully Downloaded: ', full_path_downloaded_filename)
                        else:
                            print('Image Couldn\'t be retrieved')
                else:
                    print('Image already exists : {}'.format(full_path_downloaded_filename))

            latest.append({
                "code" : code, 
                "latest_update" : latest_update
            })


# In[ ]:


if latest:
    latest_df = pd.DataFrame.from_records(latest, index=["code"])
    latest_df
    latest_df.to_csv('latest.csv', index=True)    

