import base64

chars = input("Veuillez renseigner le string en base64")

a = base64.b64decode(chars).decode().split(";")[0]

print(a)