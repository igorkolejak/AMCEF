import requests
from tkinter import *
BASE = "http://127.0.0.1:5000/"

def get():
  tmp_id = id.get()
  response = requests.get(BASE + "post/" + tmp_id)
  textarea.delete('1.0', END)
  textarea.insert(END, response.json())

def put():
  tmp_id = id.get()
  tmp_userId = userId.get()
  tmp_title = title.get()
  tmp_body = body.get()
  
  response = requests.put(BASE + "post/" + tmp_id, {"userId": int(tmp_userId), "title": tmp_title, "body": tmp_body})
  textarea.delete('1.0', END)
  textarea.insert(END, response.json())

def delete():
  tmp_id = id.get()
  response = requests.delete(BASE + "post/" + tmp_id)
  textarea.delete('1.0', END)
  textarea.insert(END, response.json())

def patch():
  tmp_id = id.get()
  tmp_title = title.get()
  tmp_body = body.get()
  
  text = {}
  is_added = False
  if tmp_title is not "":
    text['title']=tmp_title
  if tmp_body is not "":
    text['body']=tmp_body
  
  print(text)
  response = requests.patch(BASE + "post/" + tmp_id, text)
  textarea.delete('1.0', END)
  textarea.insert(END, response.json())

root = Tk()

id = StringVar()
userId = StringVar()
title = StringVar()
body = StringVar()


Label(root, text='ID: ').grid(row=0, column=0)
Entry(root, textvariable = id).grid(row=0, column=1)
Label(root, text='User ID: ').grid(row=1, column=0)
Entry(root, textvariable = userId).grid(row=1, column=1)
Label(root, text='Title: ').grid(row=2, column=0)
Entry(root, textvariable = title).grid(row=2, column=1)
Label(root, text='Body: ').grid(row=3, column=0)
Entry(root, textvariable = body).grid(row=3, column=1)

Button(text="Get", width=15, height=1, command=get).grid(column=2, row=0)
Button(text="Insert", width=15, height=1, command=put).grid(column=2, row=1)
Button(text="Delete", width=15, height=1, command=delete).grid(column=2, row=2)
Button(text="Update", width=15, height=1, command=patch).grid(column=2, row=3)

textarea = Text(root)
textarea.grid(column=0, columnspan=3, row=4)

root.mainloop()
