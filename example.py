#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import bilisuite as bls


# In[ ]:


bls.setting.up(
    usragent = "",
    cookie = "",
    csrf = ""
)


# In[ ]:


bvid = bls.search.uploader('27534330', page=10)


# In[ ]:


bls.tool.observer(bvid, 'Elysia', page=20, branch=100)


# In[ ]:


bls.tool.spammer('27534330', 'Elysia is my waifu')


# In[ ]:


bls.tool.tracer('BV1fY4y1F7GL', 48*24*30)

