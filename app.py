import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import sqlite3
import os

# Configuração da página
st.set_page_config(
    page_title="Loja de Bebidas",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="collapsed"  # Menu lateral fechado por padrão no mobile
)

# CSS customizado para mobile
st.markdown("""
<style>
    /* Otimizações para mobile */
    .stApp {
        max-width: 100%;
    }
    
    /* Botões maiores para touch */
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    /* Inputs maiores */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        font-size: 1.1rem;
        height: 3rem;
        border-radius: 10px;
    }
    
    /* Cards de métricas mais destacadas */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Títulos mais destacados */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    /* Menu lateral otimizado */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Formulários mais espaçados */
    .stForm {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Tabelas responsivas */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Gráficos responsivos */
    .plotly-graph-div {
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        
        .stButton > button {
            height: 3.5rem;
            font-size: 1.2rem;
        }
        
        .metric-container {
            padding: 1rem;
        }
    }
</style>

<!-- PWA Meta Tags -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Loja Bebidas">
<meta name="mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#667eea">
<link rel="manifest" href="/manifest.json">

<!-- PWA JavaScript -->
<script>
    // Registrar Service Worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registrado com sucesso:', registration.scope);
            }, function(err) {
                console.log('Falha ao registrar SW:', err);
            });
        });
    }
    
    // Prompt de instalação PWA
    let deferredPrompt;
    const installButton = document.createElement('button');
    installButton.style.display = 'none';
    installButton.textContent = '📱 Instalar App';
    installButton.style.position = 'fixed';
    installButton.style.bottom = '20px';
    installButton.style.right = '20px';
    installButton.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    installButton.style.color = 'white';
    installButton.style.border = 'none';
    installButton.style.padding = '15px 20px';
    installButton.style.borderRadius = '25px';
    installButton.style.fontSize = '16px';
    installButton.style.fontWeight = 'bold';
    installButton.style.cursor = 'pointer';
    installButton.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
    installButton.style.zIndex = '1000';
    
    document.body.appendChild(installButton);
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        installButton.style.display = 'block';
    });
    
    installButton.addEventListener('click', (e) => {
        installButton.style.display = 'none';
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((result) => {
            if (result.outcome === 'accepted') {
                console.log('PWA instalado');
            }
            deferredPrompt = null;
        });
    });
    
    window.addEventListener('appinstalled', (evt) => {
        console.log('PWA instalado com sucesso');
        installButton.style.display = 'none';
    });
</script>
""", unsafe_allow_html=True)

# Função para inicializar o banco de dados
def init_database():
    conn = sqlite3.connect('loja_bebidas.db')
    cursor = conn.cursor()
    
    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            data_cadastro TEXT
        )
    ''')
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            data_cadastro TEXT
        )
    ''')
    
    # Tabela de vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            cliente_id INTEGER,
            nome_produto TEXT,
            nome_cliente TEXT,
            quantidade INTEGER,
            valor_unitario REAL,
            valor_total REAL,
            data_venda TEXT,
            hora_venda TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Função para carregar clientes
def carregar_clientes():
    conn = sqlite3.connect('loja_bebidas.db')
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    return df

# Função para adicionar cliente
def adicionar_cliente(nome, telefone=""):
    conn = sqlite3.connect('loja_bebidas.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clientes (nome, telefone, data_cadastro)
        VALUES (?, ?, ?)
    ''', (nome, telefone, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

# Função para carregar produtos
def carregar_produtos():
    conn = sqlite3.connect('loja_bebidas.db')
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

# Função para carregar vendas
def carregar_vendas():
    conn = sqlite3.connect('loja_bebidas.db')
    df = pd.read_sql_query("SELECT * FROM vendas", conn)
    conn.close()
    return df

# Função para adicionar produto
def adicionar_produto(nome, categoria, preco, estoque):
    conn = sqlite3.connect('loja_bebidas.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO produtos (nome, categoria, preco, estoque, data_cadastro)
        VALUES (?, ?, ?, ?, ?)
    ''', (nome, categoria, preco, estoque, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

# Função para registrar venda
def registrar_venda(produto_id, cliente_id, nome_produto, nome_cliente, quantidade, valor_unitario):
    conn = sqlite3.connect('loja_bebidas.db')
    cursor = conn.cursor()
    
    valor_total = quantidade * valor_unitario
    data_venda = datetime.now().strftime("%Y-%m-%d")
    hora_venda = datetime.now().strftime("%H:%M:%S")
    
    cursor.execute('''
        INSERT INTO vendas (produto_id, cliente_id, nome_produto, nome_cliente, quantidade, valor_unitario, valor_total, data_venda, hora_venda)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (produto_id, cliente_id, nome_produto, nome_cliente, quantidade, valor_unitario, valor_total, data_venda, hora_venda))
    
    # Atualizar estoque
    cursor.execute('''
        UPDATE produtos SET estoque = estoque - ? WHERE id = ?
    ''', (quantidade, produto_id))
    
    conn.commit()
    conn.close()

# Inicializar banco de dados
init_database()

# Título principal com estilo mobile
st.markdown('<h1 class="main-title">🍺 Loja de Bebidas</h1>', unsafe_allow_html=True)
st.markdown("---")

# Menu lateral otimizado para mobile
st.sidebar.title("🔧 Menu")
st.sidebar.markdown("*Toque para navegar*")
opcao = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["🏠 Início", "📦 Produtos", "👥 Clientes", "🛒 Vendas", "📊 Relatórios"]
)

# ========================================
# PÁGINA INICIAL
# ========================================
if opcao == "🏠 Início":
    st.markdown("### 📊 Resumo do Negócio")
    
    # Carregar dados para estatísticas
    produtos_df = carregar_produtos()
    vendas_df = carregar_vendas()
    clientes_df = carregar_clientes()
    
    # Métricas em cards estilizados para mobile
    col1, col2, col3 = st.columns(3)
    
    with col1:
        produtos_count = len(produtos_df) if not produtos_df.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <h2>📦</h2>
            <h3>{produtos_count}</h3>
            <p>Produtos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        clientes_count = len(clientes_df) if not clientes_df.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <h2>👥</h2>
            <h3>{clientes_count}</h3>
            <p>Clientes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        faturamento = vendas_df['valor_total'].sum() if not vendas_df.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <h2>💰</h2>
            <h3>R$ {faturamento:.0f}</h3>
            <p>Faturamento</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botões de acesso rápido para mobile
    st.markdown("### ⚡ Acesso Rápido")
    st.markdown("*Use o menu lateral para navegar entre as seções*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🛒 **Nova Venda**\n\nVá ao menu → Vendas")
    
    with col2:
        st.info("📊 **Relatórios**\n\nVá ao menu → Relatórios")
    
    st.markdown("---")
    st.markdown("### 🎯 Como usar:")
    st.markdown("""
    📦 **Produtos**: Cadastre suas bebidas  
    👥 **Clientes**: Adicione seus clientes  
    🛒 **Vendas**: Registre vendas rapidamente  
    📊 **Relatórios**: Analise seu desempenho  
    """)

# ========================================
# GERENCIAR PRODUTOS
# ========================================
elif opcao == "📦 Produtos":
    st.header("📦 Gerenciamento de Produtos")
    
    tab1, tab2 = st.tabs(["➕ Cadastrar Produto", "📋 Ver Produtos"])
    
    with tab1:
        st.subheader("Cadastrar Novo Produto")
        
        with st.form("form_produto"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Produto *", placeholder="Ex: Coca-Cola 350ml")
                preco = st.number_input("Preço (R$) *", min_value=0.01, step=0.01, format="%.2f")
            
            with col2:
                categoria = st.selectbox("Categoria *", [
                    "Refrigerantes",
                    "Cervejas",
                    "Águas",
                    "Sucos",
                    "Energéticos",
                    "Vinhos",
                    "Destilados",
                    "Outros"
                ])
                estoque = st.number_input("Quantidade em Estoque *", min_value=0, step=1)
            
            submitted = st.form_submit_button("✅ Cadastrar Produto", type="primary")
            
            if submitted:
                if nome and preco and categoria and estoque >= 0:
                    adicionar_produto(nome, categoria, preco, estoque)
                    st.success(f"✅ Produto '{nome}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios!")
    
    with tab2:
        st.subheader("Produtos Cadastrados")
        
        produtos_df = carregar_produtos()
        
        if not produtos_df.empty:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                categorias = ["Todas"] + list(produtos_df['categoria'].unique())
                filtro_categoria = st.selectbox("Filtrar por Categoria:", categorias)
            
            with col2:
                busca_nome = st.text_input("Buscar por Nome:", placeholder="Digite o nome do produto")
            
            # Aplicar filtros
            df_filtrado = produtos_df.copy()
            if filtro_categoria != "Todas":
                df_filtrado = df_filtrado[df_filtrado['categoria'] == filtro_categoria]
            if busca_nome:
                df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(busca_nome, case=False, na=False)]
            
            # Exibir tabela
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado[['nome', 'categoria', 'preco', 'estoque', 'data_cadastro']],
                    column_config={
                        "nome": "Produto",
                        "categoria": "Categoria",
                        "preco": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
                        "estoque": "Estoque",
                        "data_cadastro": "Data Cadastro"
                    },
                    use_container_width=True
                )
                
                # Alertas de estoque baixo
                estoque_baixo = df_filtrado[df_filtrado['estoque'] <= 5]
                if not estoque_baixo.empty:
                    st.warning("⚠️ **Produtos com estoque baixo (≤ 5 unidades):**")
                    for _, produto in estoque_baixo.iterrows():
                        st.write(f"• {produto['nome']}: {produto['estoque']} unidades")
            else:
                st.info("Nenhum produto encontrado com os filtros aplicados.")
        else:
            st.info("📦 Nenhum produto cadastrado ainda. Use a aba 'Cadastrar Produto' para começar!")

# ========================================
# GERENCIAR CLIENTES
# ========================================
elif opcao == "👥 Clientes":
    st.header("👥 Gerenciamento de Clientes")
    
    tab1, tab2 = st.tabs(["➕ Cadastrar Cliente", "📋 Ver Clientes"])
    
    with tab1:
        st.subheader("Cadastrar Novo Cliente")
        
        with st.form("form_cliente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_cliente = st.text_input("Nome do Cliente *", placeholder="Ex: João da Silva")
            
            with col2:
                telefone_cliente = st.text_input("Telefone (Opcional)", placeholder="Ex: (11) 99999-9999")
            
            submitted = st.form_submit_button("✅ Cadastrar Cliente", type="primary")
            
            if submitted:
                if nome_cliente.strip():
                    adicionar_cliente(nome_cliente.strip(), telefone_cliente.strip())
                    st.success(f"✅ Cliente '{nome_cliente}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Por favor, digite o nome do cliente!")
    
    with tab2:
        st.subheader("Clientes Cadastrados")
        
        clientes_df = carregar_clientes()
        
        if not clientes_df.empty:
            # Filtro por nome
            busca_cliente = st.text_input("Buscar Cliente:", placeholder="Digite o nome do cliente")
            
            # Aplicar filtro
            df_filtrado = clientes_df.copy()
            if busca_cliente:
                df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(busca_cliente, case=False, na=False)]
            
            # Exibir tabela
            if not df_filtrado.empty:
                st.dataframe(
                    df_filtrado[['nome', 'telefone', 'data_cadastro']],
                    column_config={
                        "nome": "Nome do Cliente",
                        "telefone": "Telefone",
                        "data_cadastro": "Data Cadastro"
                    },
                    use_container_width=True
                )
                
                st.info(f"📊 Total de clientes: {len(df_filtrado)}")
            else:
                st.info("Nenhum cliente encontrado com o filtro aplicado.")
        else:
            st.info("👥 Nenhum cliente cadastrado ainda. Use a aba 'Cadastrar Cliente' para começar!")

# ========================================
# REGISTRAR VENDAS
# ========================================
elif opcao == "🛒 Vendas":
    st.header("🛒 Registrar Vendas")
    
    produtos_df = carregar_produtos()
    clientes_df = carregar_clientes()
    
    if produtos_df.empty:
        st.warning("⚠️ Você precisa cadastrar produtos antes de registrar vendas!")
        st.info("Vá para 'Gerenciar Produtos' → 'Cadastrar Produto'")
    elif clientes_df.empty:
        st.warning("⚠️ Você precisa cadastrar clientes antes de registrar vendas!")
        st.info("Vá para 'Gerenciar Clientes' → 'Cadastrar Cliente'")
    else:
        # Filtrar apenas produtos com estoque > 0
        produtos_disponiveis = produtos_df[produtos_df['estoque'] > 0]
        
        if produtos_disponiveis.empty:
            st.error("❌ Não há produtos com estoque disponível!")
        else:
            with st.form("form_venda"):
                st.subheader("Nova Venda")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Selectbox com clientes
                    opcoes_clientes = [f"{row['nome']}" + (f" - {row['telefone']}" if row['telefone'] else "") 
                                     for _, row in clientes_df.iterrows()]
                    cliente_selecionado = st.selectbox("Selecionar Cliente *", opcoes_clientes)
                    
                    # Encontrar o cliente selecionado
                    nome_cliente = cliente_selecionado.split(" - ")[0]
                    cliente = clientes_df[clientes_df['nome'] == nome_cliente].iloc[0]
                
                with col2:
                    # Selectbox com produtos disponíveis
                    opcoes_produtos = [f"{row['nome']} (Estoque: {row['estoque']}) - R$ {row['preco']:.2f}" 
                                     for _, row in produtos_disponiveis.iterrows()]
                    produto_selecionado = st.selectbox("Selecionar Produto *", opcoes_produtos)
                    
                    # Encontrar o produto selecionado
                    nome_produto = produto_selecionado.split(" (Estoque:")[0]
                    produto = produtos_disponiveis[produtos_disponiveis['nome'] == nome_produto].iloc[0]
                
                # Quantidade
                max_quantidade = int(produto['estoque'])
                quantidade = st.number_input(
                    f"Quantidade * (Máximo: {max_quantidade})", 
                    min_value=1, 
                    max_value=max_quantidade, 
                    step=1
                )
                
                # Mostrar resumo da venda
                valor_total = quantidade * produto['preco']
                st.info(f"💰 **Resumo da Venda:**\n"
                       f"Cliente: {cliente['nome']}\n"
                       f"Produto: {produto['nome']}\n"
                       f"Quantidade: {quantidade}\n"
                       f"Valor Unitário: R$ {produto['preco']:.2f}\n"
                       f"**Valor Total: R$ {valor_total:.2f}**")
                
                submitted = st.form_submit_button("✅ Confirmar Venda", type="primary")
                
                if submitted:
                    registrar_venda(produto['id'], cliente['id'], produto['nome'], cliente['nome'], quantidade, produto['preco'])
                    st.success(f"✅ Venda registrada com sucesso!\n"
                             f"Cliente: {cliente['nome']}\n"
                             f"Total: R$ {valor_total:.2f}")
                    st.balloons()
                    st.rerun()

# ========================================
# DASHBOARD & RELATÓRIOS
# ========================================
elif opcao == "📊 Relatórios":
    st.header("📊 Dashboard & Relatórios")
    
    vendas_df = carregar_vendas()
    produtos_df = carregar_produtos()
    
    if vendas_df.empty:
        st.warning("⚠️ Nenhuma venda registrada ainda!")
        st.info("Registre algumas vendas para ver os relatórios aqui.")
    else:
        # Filtros por período
        st.sidebar.markdown("### 📅 Filtros de Período")
        vendas_df['data_venda'] = pd.to_datetime(vendas_df['data_venda'])
        
        data_inicio = st.sidebar.date_input("Data Início", vendas_df['data_venda'].min().date())
        data_fim = st.sidebar.date_input("Data Fim", vendas_df['data_venda'].max().date())
        
        # Filtrar dados por período
        mask = (vendas_df['data_venda'].dt.date >= data_inicio) & (vendas_df['data_venda'].dt.date <= data_fim)
        vendas_filtradas = vendas_df.loc[mask]
        
        if vendas_filtradas.empty:
            st.warning("Nenhuma venda encontrada no período selecionado.")
        else:
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Vendas no Período", len(vendas_filtradas))
            with col2:
                st.metric("Faturamento", f"R$ {vendas_filtradas['valor_total'].sum():.2f}")
            with col3:
                st.metric("Ticket Médio", f"R$ {vendas_filtradas['valor_total'].mean():.2f}")
            with col4:
                st.metric("Itens Vendidos", vendas_filtradas['quantidade'].sum())
            
            st.markdown("---")
            
            # Gráficos
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Vendas por Dia", "🏆 Top Produtos", "👥 Top Clientes", "💰 Faturamento", "📊 Por Categoria"])
            
            with tab1:
                st.subheader("Vendas por Dia")
                vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas['data_venda'].dt.date).agg({
                    'valor_total': 'sum',
                    'quantidade': 'sum'
                }).reset_index()
                
                fig = px.line(vendas_por_dia, x='data_venda', y='valor_total', 
                            title='Faturamento Diário',
                            labels={'data_venda': 'Data', 'valor_total': 'Faturamento (R$)'})
                fig.update_traces(line_color='#1f77b4', line_width=3)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("Top 10 Produtos Mais Vendidos")
                top_produtos = vendas_filtradas.groupby('nome_produto').agg({
                    'quantidade': 'sum',
                    'valor_total': 'sum'
                }).reset_index().sort_values('quantidade', ascending=False).head(10)
                
                fig = px.bar(top_produtos, x='quantidade', y='nome_produto', 
                           title='Produtos Mais Vendidos (Quantidade)',
                           labels={'quantidade': 'Quantidade Vendida', 'nome_produto': 'Produto'},
                           orientation='h')
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("Top 10 Melhores Clientes")
                top_clientes = vendas_filtradas.groupby('nome_cliente').agg({
                    'valor_total': 'sum',
                    'quantidade': 'sum'
                }).reset_index().sort_values('valor_total', ascending=False).head(10)
                
                fig = px.bar(top_clientes, x='valor_total', y='nome_cliente', 
                           title='Clientes que Mais Gastam (Faturamento)',
                           labels={'valor_total': 'Total Gasto (R$)', 'nome_cliente': 'Cliente'},
                           orientation='h')
                fig.update_traces(marker_color='green')
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela com informações detalhadas dos clientes
                if not top_clientes.empty:
                    st.markdown("#### 📋 Detalhes dos Top Clientes")
                    top_clientes['ticket_medio'] = top_clientes['valor_total'] / top_clientes['quantidade']
                    st.dataframe(
                        top_clientes,
                        column_config={
                            "nome_cliente": "Cliente",
                            "quantidade": "Itens Comprados",
                            "valor_total": st.column_config.NumberColumn("Total Gasto", format="R$ %.2f"),
                            "ticket_medio": st.column_config.NumberColumn("Ticket Médio", format="R$ %.2f")
                        },
                        use_container_width=True
                    )
            
            with tab5:
                st.subheader("Análise de Faturamento")
                top_faturamento = vendas_filtradas.groupby('nome_produto')['valor_total'].sum().reset_index().sort_values('valor_total', ascending=False).head(10)
                
                fig = px.pie(top_faturamento, values='valor_total', names='nome_produto',
                           title='Distribuição do Faturamento por Produto')
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.subheader("Vendas por Categoria")
                # Merge com produtos para obter categoria
                vendas_com_categoria = vendas_filtradas.merge(produtos_df[['id', 'categoria']], 
                                                            left_on='produto_id', right_on='id', how='left')
                
                vendas_categoria = vendas_com_categoria.groupby('categoria').agg({
                    'valor_total': 'sum',
                    'quantidade': 'sum'
                }).reset_index()
                
                fig = px.bar(vendas_categoria, x='categoria', y='valor_total',
                           title='Faturamento por Categoria',
                           labels={'categoria': 'Categoria', 'valor_total': 'Faturamento (R$)'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de vendas detalhadas
            st.markdown("---")
            st.subheader("📋 Histórico Detalhado de Vendas")
            
            vendas_display = vendas_filtradas[['data_venda', 'hora_venda', 'nome_cliente', 'nome_produto', 'quantidade', 'valor_unitario', 'valor_total']].copy()
            vendas_display['data_venda'] = vendas_display['data_venda'].dt.strftime('%d/%m/%Y')
            
            st.dataframe(
                vendas_display,
                column_config={
                    "data_venda": "Data",
                    "hora_venda": "Hora",
                    "nome_cliente": "Cliente",
                    "nome_produto": "Produto",
                    "quantidade": "Qtd",
                    "valor_unitario": st.column_config.NumberColumn("Valor Unit.", format="R$ %.2f"),
                    "valor_total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f")
                },
                use_container_width=True
            )

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🍺 Sistema de Gestão para Loja de Bebidas | Desenvolvido para otimizar suas vendas"
    "</div>", 
    unsafe_allow_html=True
)
