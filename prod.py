import json
import pprint
import sys


class FormatPrinter(pprint.PrettyPrinter):
    def __init__(self, formats):
        super(FormatPrinter, self).__init__()
        self.formats = formats

    def format(self, obj, ctx, maxlvl, lvl):
        if type(obj) in self.formats:
            return self.formats[type(obj)] % obj, 1, 0
        return pprint.PrettyPrinter.format(self, obj, ctx, maxlvl, lvl)


class Touille:
    def __init__(self, matieres, commandes):
        self.ingredients = {}
        self.matieres = self.load_json("matieres")
        self.commandes = self.load_json("commandes")

    def load_json(self, basename):
        try:
            json_data = open(basename + ".json", "r")
        except Exception:
            print(f"{basename}.json non trouvé")
            sys.exit(1)
        try:
            return json.load(json_data)
        except json.decoder.JSONDecodeError as e:
            print(f"erreur de syntaxe dans le fichier {basename}.json (\"{e}\")")
            sys.exit(2)

    def detail(self, produit, quantite):
        if produit in self.matieres:
            return self.matieres[produit]["prix"] * quantite
        else:
            recette = self.load_json(produit)
            facteur = sum(recette["ingredients"].values())
            quantite *= recette.get("taux-perte", 1)
            quantite *= recette.get("poids-paton", 1)
            if produit not in self.ingredients:
                self.ingredients[produit] = {"recette": {}}
            prix = 0
            for ingredient, quantite_ingredient in recette["ingredients"].items():
                quantite_ingredient = (quantite * quantite_ingredient) / facteur
                quantite_ingredient += recette.pop("securite", 0)
                if ingredient in self.ingredients[produit]["recette"]:
                    self.ingredients[produit]["recette"][ingredient] += quantite_ingredient
                else:
                    self.ingredients[produit]["recette"][ingredient] = quantite_ingredient
                prix += self.detail(ingredient, quantite_ingredient)
            self.ingredients[produit]["poids-total"] = sum(self.ingredients[produit]["recette"].values())
            self.ingredients[produit]["prix"] = prix
            return prix

    def touille(self):
        for commande, quantite_commande in self.commandes.items():
            self.detail(commande, quantite_commande)
        FormatPrinter({float: "%.4f"}).pprint(self.ingredients)


if __name__ == "__main__":
    touille = Touille("matieres", "commandes")
    touille.touille()