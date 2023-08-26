#!/usr/bin/env python
# coding: utf-8

# ### CRAWL ALL THE COMMENTS FROM ONE UPLOADER
# I used Honkai Impact 3rd official account as an example

# In[ ]:


import bilisuite as bls


# In[ ]:


# find the mid from uploader's profile page
# ex. https://space.bilibili.com/27534330/
bvid = bls.search.uploader('27534330')


# In[ ]:


bvid


# In[ ]:


# crawling comments takes a long time (10 hours for me to get it done)
bls.tool.observer(bvid, 'honkai3rd')


# ### LABEL THE DATA ON YOUR OWN
# 1. Make sure you labelled at least 200 bad comment
# 2. I used '1' for comments that are against community rules and '0' for any others

# In[ ]:


import pandas as pd
df = bls.process.std(pd.read_csv('train.csv')) # format the raw data and split sentence to words
train = pd.concat([df[df['rating']==i].sample(200) for i in [0,1]]) # create equaly splited dataset


# In[ ]:


# load stopword
with open('stopword.txt') as file:
    stopword = file.readline().split(',')


# In[ ]:


# vectorize comments
from sklearn.feature_extraction.text import CountVectorizer
count = CountVectorizer(token_pattern='[\u4e00-\u9fa5]{1,}', stop_words=stopword)
bow = count.fit_transform(train['comment'])


# In[ ]:


x = bow.toarray()
y = train['rating']


# In[ ]:


# shuffle them and split out a test set, though it's not mandatory
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(x, y, test_size=0.1, random_state=6)


# In[ ]:


# train the model, try to get this above 85%
from sklearn.svm import SVC
lab = SVC()
lab.fit(x_train, y_train)
lab.score(x_test, y_test)


# In[ ]:


# convert the whole comment dataset, so that the modal understands
comment = count.transform(df['comment']).toarray()

# get the prediction and add to the main dataset
df['predict'] = lab.predict(comment)

# find the rpids that got a bad prediction on their comment
target = df.loc[df['predict']==1, 'rpid']


# In[ ]:


# find it yourself from webpage, make sure you are logged in
bls.setting.up(
    cookie = "",
    csrf = ""
)


# In[ ]:


import time

# let's go!!!
for rpid in target:
    try:
        print(rpid, end=': ')
        code = bls.post.report(rpid)
        print(bls.utils.code2msg(code))
    except Exception as error:
        print(error)
    finally:
        # don't speed it up
        time.sleep(180)

