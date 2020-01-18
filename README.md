# SimpleChatBot
Version 1

初步的成分匹配，可以匹配一定的词语成分
 
如果找到一样的问句，并且其中词语成分一致的情况下，才所有的答句中随机选择一句进行回话
 

指令
```
教导词语：进入教导词语模式，从而告诉机器人某些词语属于什么类型
教导句子：进入教导句子模式，从而教会机器人句子
聊天：进入聊天模式，让机器人回应你说的话，如果没有找到，则当场进行询问
```

```
你:教导词语
机器人：进入词语学习模式
机器人：你想教我什么类型的词语？
你:人名
机器人：这种类型的词语有哪些呢？(使用空格分隔)
你:小明
机器人：我明白了！你还想教我什么类型的单词吗？
你:水果
机器人：这种类型的词语有哪些呢？(使用空格分隔)
你:苹果
机器人：我明白了！你还想教我什么类型的单词吗？
你:教导句子
机器人：进入句子学习模式
你:[人名]喜欢[水果]吗？
机器人：我应该怎么回复？
你:喜欢
机器人：我明白了！
你:聊天
机器人：进入聊天模式
你:小明喜欢苹果吗？
机器人：喜欢
你:旺财喜欢苹果吗？
机器人：我不太明白，遇上这样的句子我应该怎么回复？
```