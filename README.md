# BiliBili-Community-Suite

Import it to your python program
```python
import bilisuite as bls
```

Module dependency
```shell
pip3 install -r requirements.txt
```

The main file is [bilisuite.py](bilisuite.py), while the others are the applications. You can also build your own tools based on this module, and methods are pretty straight forward. I developped all these using google chrome, and I suggest you to stick with it in case weird problems occured. Also, the website changes all the time, so the program might fail at any time. (espeically the `bls.load.data`, which allows user get video data, because BiliBili is about to change vidoe data information in the near future) The followings are some tools I provide.

1. Protecter (see [protecter.ipynb](protector.ipynb))
2. Tracer (see [example.ipynb](example.ipynb))
3. Observer (see [example.ipynb](example.ipynb))
4. Spammer (see [example.ipynb](example.ipynb))

## Protector Tool Introduction

This tools is for detecting comments that are against community rules, and reporting them. It is the ultimate application of bilisuite, and you need to know about `pandas` and `sklearn` to use it. Here is the work flow.

1. The tool helps you crawl all the comments from an uploader or a list of videos (about 1-10% loss due to api issues), and it might takes to hours to finish depending on the size. For my own testing, I got 400k comments in 5-6 hours.
2. You can generate a smaller dataset to label (10k comments are good enough for labelling), so that Execel or Numbers can handle them easily. Since I have set the default label as `0`(good, so no reporting), which most comments are, you can finish labelling in an hour. 
3. After labelling, you equaly split them, vectorize them and throw them to a model (I used SVM here just to keep it simple). After the spliting step, you should have a relatively small dataset, so that the model trains it really fast.
4. Lastly, you use the model the predict the whole dataset. For each that is predicted as bad (against community rule), you report them by the method `bls.post.report`. Between every report, you should wait about 180s, so that the platform won't say you report too fast. (though 180s is still not stable) If the report failed, the tool will skip that one to the next. You can modify this part, so it can keep a record of failed reports for another shot later.

I got the idea of building this tool due to a game called Honkai Impact 3rd. There was once a period that people were having extremely critical words on the game for some ridiculous reasons. Many people who stood for the game got tons of cyber violence, and I think it was freaking insane. However, good thing was that the game saved itself by its quality later. However, this was not my first time witnessing these, so I decided to do something to clean up the community a bit.
