import os
import django
import sys

import sys
import io

# Set up Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_system.settings')
django.setup()

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.models import GotovayaProdukcia, Ingredienty

def list_recipes():
    print("--- Список рецептов продукции ---")
    products = GotovayaProdukcia.objects.all()
    if not products.exists():
        print("Продукция не найдена.")
        return

    for product in products:
        print(f"\nТовар: {product.name} ({product.id_edizm.name})")
        ingredients = Ingredienty.objects.filter(id_produkcii=product)
        if not ingredients.exists():
            print("  Рецепт не задан.")
        else:
            for ing in ingredients:
                print(f"  - {ing.id_syrya.name}: {ing.quantity} {ing.id_syrya.id_edizm.name}")

if __name__ == "__main__":
    list_recipes()
