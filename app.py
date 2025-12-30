import streamlit as st
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(page_title="Sistema Docis Gourmet", layout="wide")
st.title("🍬 Sistema de Precificação: Docis Gourmet")

# --- Inicialização do Banco de Dados (Session State) ---
if 'insumos' not in st.session_state:
    # Dados iniciais baseados nos seus CSVs
    st.session_state.insumos = pd.DataFrame([
        {"Ingrediente": "Leite Condensado", "Preço_Pagamento": 6.50, "Peso_Total_g": 395},
        {"Ingrediente": "Creme de Leite", "Preço_Pagamento": 3.00, "Peso_Total_g": 200},
        {"Ingrediente": "Chocolate Nobre", "Preço_Pagamento": 45.00, "Peso_Total_g": 1000},
        {"Ingrediente": "Manteiga Extra", "Preço_Pagamento": 12.00, "Peso_Total_g": 200},
        {"Ingrediente": "Forminha nº4 (unid)", "Preço_Pagamento": 0.05, "Peso_Total_g": 1}, # Peso 1 para ser unitário
    ])

if 'config' not in st.session_state:
    st.session_state.config = {
        "salario_desejado": 3000.00,
        "horas_trabalhadas": 160, # Mensal
        "custos_fixos": 500.00, # Água, luz, internet
        "lucro_padrao": 100.0
    }

# --- FUNÇÕES AUXILIARES ---
def calcular_custo_minuto():
    cfg = st.session_state.config
    custo_total_empresa = cfg["salario_desejado"] + cfg["custos_fixos"]
    minutos_mes = cfg["horas_trabalhadas"] * 60
    return custo_total_empresa / minutes_mes if minutes_mes > 0 else 0

# --- BARRA LATERAL (NAVEGAÇÃO) ---
menu = st.sidebar.radio("Navegação", ["Dashboard & Configurações", "Gerenciar Insumos", "Criar Ficha Técnica"])

# --- PÁGINA 1: DASHBOARD & CONFIGURAÇÕES ---
if menu == "Dashboard & Configurações":
    st.header("⚙️ Configurações da Empresa")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.config["salario_desejado"] = st.number_input("Salário Desejado (Mensal)", value=st.session_state.config["salario_desejado"])
        st.session_state.config["horas_trabalhadas"] = st.number_input("Horas Trabalhadas (Mensal)", value=st.session_state.config["horas_trabalhadas"])
    
    with col2:
        st.session_state.config["custos_fixos"] = st.number_input("Custos Fixos (Gás, Luz, etc)", value=st.session_state.config["custos_fixos"])
        st.session_state.config["lucro_padrao"] = st.number_input("Margem de Lucro Padrão (%)", value=st.session_state.config["lucro_padrao"])
        
    valor_minuto = calcular_custo_minuto()
    
    with col3:
        st.info(f"💰 Valor do seu Minuto: R$ {valor_minuto:.2f}")
        st.markdown("*Este valor será usado para calcular o custo de mão de obra em cada receita.*")

# --- PÁGINA 2: GERENCIAR INSUMOS ---
elif menu == "Gerenciar Insumos":
    st.header("📦 Cadastro de Ingredientes e Embalagens")
    
    with st.form("add_insumo"):
        col_a, col_b, col_c = st.columns(3)
        nome = col_a.text_input("Nome do Item")
        preco = col_b.number_input("Preço Pago (R$)", min_value=0.01, format="%.2f")
        peso = col_c.number_input("Peso/Qtd na Embalagem (g ou un)", min_value=1.0)
        
        submitted = st.form_submit_button("Adicionar Insumo")
        
        if submitted and nome:
            novo_insumo = {"Ingrediente": nome, "Preço_Pagamento": preco, "Peso_Total_g": peso}
            st.session_state.insumos = pd.concat([st.session_state.insumos, pd.DataFrame([novo_insumo])], ignore_index=True)
            st.success(f"{nome} adicionado!")

    # Exibir Tabela com Cálculo Automático
    df = st.session_state.insumos.copy()
    df['Custo por Grama/Un'] = df['Preço_Pagamento'] / df['Peso_Total_g']
    st.dataframe(df, use_container_width=True)

# --- PÁGINA 3: CRIAR FICHA TÉCNICA (CALCULADORA) ---
elif menu == "Criar Ficha Técnica":
    st.header("🍰 Calculadora de Preço de Venda")
    
    col_rec1, col_rec2 = st.columns(2)
    nome_receita = col_rec1.text_input("Nome do Produto (Ex: Cento Brigadeiro Ninho)")
    rendimento = col_rec2.number_input("Rendimento (Quantas unidades rende?)", min_value=1, value=100)
    tempo_preparo = col_rec1.number_input("Tempo de Preparo (minutos)", min_value=10, value=60)
    
    st.divider()
    
    # Seleção de Ingredientes
    st.subheader("Ingredientes da Receita")
    
    if 'receita_atual' not in st.session_state:
        st.session_state.receita_atual = []
        
    col_ing1, col_ing2, col_ing3 = st.columns([3, 1, 1])
    ingrediente_sel = col_ing1.selectbox("Escolha o Ingrediente", st.session_state.insumos['Ingrediente'].unique())
    qtd_usada = col_ing2.number_input("Qtd (g ou un)", min_value=0.0)
    
    if col_ing3.button("Adicionar"):
        # Buscar dados do insumo
        dados_insumo = st.session_state.insumos[st.session_state.insumos['Ingrediente'] == ingrediente_sel].iloc[0]
        custo_grama = dados_insumo['Preço_Pagamento'] / dados_insumo['Peso_Total_g']
        custo_item = custo_grama * qtd_usada
        
        st.session_state.receita_atual.append({
            "Ingrediente": ingrediente_sel,
            "Qtd": qtd_usada,
            "Custo Total": custo_item
        })
        
    # Mostrar lista da receita atual
    if st.session_state.receita_atual:
        df_receita = pd.DataFrame(st.session_state.receita_atual)
        st.table(df_receita)
        
        # --- CÁLCULOS FINAIS ---
        custo_materiais = df_receita['Custo Total'].sum()
        custo_mao_obra = tempo_preparo * calcular_custo_minuto()
        
        # Custos Indiretos (Gás/Luz Proporcional ao tempo - Simplificação: 10% do MO ou valor fixo)
        custo_indireto = custo_mao_obra * 0.10 
        
        custo_total_receita = custo_materiais + custo_mao_obra + custo_indireto
        custo_unitario = custo_total_receita / rendimento
        
        # Precificação
        margem = st.slider("Margem de Lucro Desejada (%)", 0, 300, int(st.session_state.config["lucro_padrao"]))
        preco_venda = custo_total_receita * (1 + (margem/100))
        preco_venda_unitario = preco_venda / rendimento
        
        st.divider()
        st.subheader("📊 Resultado Financeiro")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Custo Materiais", f"R$ {custo_materiais:.2f}")
        c2.metric("Mão de Obra + Gás", f"R$ {(custo_mao_obra + custo_indireto):.2f}")
        c3.metric("Custo Total Receita", f"R$ {custo_total_receita:.2f}")
        c4.metric("Custo Unitário", f"R$ {custo_unitario:.2f}")
        
        st.success(f"### Preço de Venda Sugerido: R$ {preco_venda:.2f}")
        st.caption(f"Isso equivale a R$ {preco_venda_unitario:.2f} por unidade/brigadeiro.")
        
        if st.button("Limpar Receita"):
            st.session_state.receita_atual = []
            st.rerun()
