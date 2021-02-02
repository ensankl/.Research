text = "a\u3000 b\t\nc\r\n"
table = str.maketrans({
  '\u3000': '',
  ' ': '',
  '\t': ''
})
text = text.translate(table)

print(text)