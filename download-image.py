#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import pandas as pd
import os
from urllib.parse import urljoin
import asyncio
import aiohttp


# In[ ]:


output_directory = os.path.join(os.getcwd(), 'output')
image_output_directory = os.path.join(os.getcwd(), 'image')
thermal_image_directory = os.path.join(image_output_directory, 'thermal')
so2_image_directory = os.path.join(image_output_directory, 'so2')

static_url = 'http://mounts-project.com/static/'


# In[ ]:


if (not os.path.exists(image_output_directory)):
    os.mkdir(image_output_directory)
    
if (not os.path.exists(thermal_image_directory)):
    os.mkdir(thermal_image_directory)
    
if (not os.path.exists(so2_image_directory)):
    os.mkdir(so2_image_directory)


# In[ ]:


df_files = pd.read_excel('output.xlsx')


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


for key in dataframes.keys():
    volcano_name = dataframes[key]['volcano_name']
    df = dataframes[key]['df']
    latest_update = dataframes[key]['latest_update']
    
    async with aiohttp.ClientSession() as session:
        for index in df.index:
            sub_image_directory = df['Type'][index].lower()
            download_dir = os.path.join(image_output_directory, sub_image_directory, volcano_name)
            os.makedirs(download_dir, exist_ok=True)

            image_path_url = df['Graph'][index]
            url = urljoin(static_url, image_path_url)
            downloaded_filename = url.split("/")[-1]
            full_path_downloaded_filename = os.path.join(download_dir, downloaded_filename)

            async with session.get(url) as response:
                image = await response.read()

                if response.ok:
                    with open(full_path_downloaded_filename, 'wb') as f:
                        f.write(image)
                        print('Image sucessfully Downloaded: ', full_path_downloaded_filename)
                else:
                    print('Image Couldn\'t be retrieved')


# In[ ]:





# In[ ]:




