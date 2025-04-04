import tkinter as tk
from tkinter import ttk

# Fonction pour mettre à jour la valeur de la StringVar
def update_label():
    elementVariable.set("Valeur mise à jour!")

# Créer la fenêtre principale
root = tk.Tk()
root.title("Exemple StringVar avec Label")

# Créer une StringVar et un Label associé
elementVariable = tk.StringVar(value="Valeur initiale")

# Créer le Label qui utilise la StringVar
label = ttk.Label(root, textvariable=elementVariable)
label.pack(padx=10, pady=10)

# Créer un bouton pour mettre à jour la StringVar
button = ttk.Button(root, text="Mettre à jour", command=update_label)
button.pack(padx=10, pady=10)



# Démarrer la boucle principale de Tkinter
#root.mainloop()
while(1):
    root.update()
