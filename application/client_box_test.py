#!/usr/bin/python
import boxdotnet

client = boxdotnet.BoxDotNet()

file_id = client.upload('test.txt')

client.replace(file_id, 'test.txt')

#client.delete(file_id)

client.download(file_id, 'tt.txt')


