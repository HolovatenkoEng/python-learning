man = {
    "skin": ["brown", "Negga", "Loser"],
    "hair": "black",
    "height": 180,
    "weight": 75
}


man["skin"].append(list(input("Enter skin color: ")))



print(str(len(man["skin"])) + " Out of 10")





if len(man["skin"]) < 10:
    print("You are fucking ugly guy!!!!!")

elif len(man["skin"]) > 10:
    print("You are bad looking guy!!!!!")

else:
    print("You are handsome guy!!!!!")



























