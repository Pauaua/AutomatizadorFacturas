import pandas as pd
import os

def generate_template():
    data = {
        'RUT_EMPRESA': ['76.123.456-7', '77.987.654-3'],
        'RUT_USUARIO': ['12.345.678-9', '09.876.543-2'],
        'CLAVE_SII': ['clave123', 'otraclave456']
    }
    df = pd.DataFrame(data)
    
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    template_path = os.path.join(assets_dir, 'template_masivo.xlsx')
    df.to_excel(template_path, index=False)
    print(f"✅ Plantilla creada en: {template_path}")

if __name__ == "__main__":
    generate_template()
