import pandas as pd
import sys

def analisar_planilha(caminho):
    try:
        print(f"📊 Analisando planilha: {caminho}")
        print("=" * 60)
        
        # Ler a planilha
        df = pd.read_excel(caminho)
        
        # Informações básicas
        print(f"📏 Dimensões: {df.shape[0]} linhas × {df.shape[1]} colunas")
        print()
        
        # Colunas encontradas
        print("📋 Colunas encontradas:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        print()
        
        # Tipos de dados
        print("🔢 Tipos de dados:")
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            print(f"  • {col}: {dtype} ({non_null}/{len(df)} não nulos)")
        print()
        
        # Primeiras linhas
        print("👀 Primeiras 5 linhas:")
        print(df.head().to_string())
        print()
        
        # Verificar se há valores nulos importantes
        print("❓ Análise de valores nulos:")
        null_counts = df.isnull().sum()
        for col, null_count in null_counts.items():
            if null_count > 0:
                percent = (null_count / len(df)) * 100
                print(f"  • {col}: {null_count} nulos ({percent:.1f}%)")
        
        if null_counts.sum() == 0:
            print("  ✅ Sem valores nulos")
        
        print()
        print("✅ Análise concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao analisar planilha: {e}")
        return False
    
    return True

if __name__ == "__main__":
    caminho_arquivo = r"C:\Users\Usuario\Downloads\LIVRO CAIXA IBINOVI - ANO 2026.xlsx"
    analisar_planilha(caminho_arquivo)
