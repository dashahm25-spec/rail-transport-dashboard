#Підключаємо бібліотеки
import streamlit as st
import pandas as pd
import plotly.express as px

# Налаштування сторінки на всю ширину
st.set_page_config(
    page_title="Rail Transport Infrastructure",
    layout="wide"
)

# Головний заголовок сторінки
st.title("Rail Transport Infrastructure")

# Завантаження та підготовка даних
def load_data():
    df = pd.read_csv("data_RailTransport.csv")
    
    #За допомогою pd.to_numeric(..., errors='coerce') примусово перетворюємо значення на числа, а всі символи по типу "?" перетворюються на (NaN)
    df['End Year Clean'] = pd.to_numeric(df['End Year'], errors='coerce')
    
    # Словник для зіставлення країн із частинами світу
    continents = {
        'Canada': 'Північна Америка',
        'US': 'Північна Америка',
        'France': 'Європа',
        'Italy': 'Європа',
        'Sweden': 'Європа',
        'UK': 'Європа',
        'Germany': 'Європа',
        'Denmark': 'Європа',
        'Norway': 'Європа',
        'Spain': 'Європа',
        'Australia': 'Океанія / Австралія',
        'Singapore': 'Азія',
        'Japan': 'Азія',
        'South Korea': 'Азія'
    }
    df['Continent'] = df['Country'].map(continents).fillna('Інше')
    
    # Очищення даних: зводимо всі залізниці лише до двох типів — Urban або Suburban
    df['Environment_Clean'] = df['Environment'].replace({
        'Paris-Nogent-sur-Seine': 'Suburban'
    })
    
    return df

df = load_data()

#Додавання даних з 2.6
def load_economics_data():
    gdp = pd.read_csv('gdp_per_capita.csv.csv', skiprows=4)
    economics_df = gdp[['Country Name', 'Country Code', '2022']].copy()
    economics_df.rename(columns={'2022': 'GDP per capita'}, inplace=True)
    
    unemployment = pd.read_csv('unemployment.csv', skiprows=4)[['Country Code', '2022']].rename(columns={'2022': 'Unemployment'})
    inflation = pd.read_csv('inflation.csv', skiprows=4)[['Country Code', '2022']].rename(columns={'2022': 'Inflation'})
    life_expectancy = pd.read_csv('life_expectancy.csv', skiprows=4)[['Country Code', '2022']].rename(columns={'2022': 'Life expectancy'})
    internet_users = pd.read_csv('internet_users.csv', skiprows=4)[['Country Code', '2022']].rename(columns={'2022': 'Internet users'})
    
    for data in [unemployment, inflation, life_expectancy, internet_users]:
        economics_df = economics_df.merge(data, on='Country Code', how='left')
        
    eu_countries = [
        'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK',
        'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'IRL',
        'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 'POL',
        'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'
    ]
    economics_df['EU member'] = economics_df['Country Code'].isin(eu_countries).map({True: 'Країна ЄС', False: 'Не в ЄС'})
    economics_df = economics_df.dropna(subset=['GDP per capita'])
    return economics_df

df_econ = load_economics_data()


# бокова панель зліва
st.sidebar.header("Параметри фільтрації")
st.sidebar.write("Використовуйте ці фільтри для перегляду залізниць у другій вкладці:")

#  Випадаючий список кількості станцій (4 діапазони)
station_choice = st.sidebar.selectbox(
    "Оберіть кількість станцій залізниці:",
    options=["Всі значення", "1 - 10", "11 - 30", "31 - ..."]
)

#За допомогою st.sidebar.radio(...) створюємо селектор частин світу (радіокнопка)
continent_list = ["Всі регіони"] + sorted(df['Continent'].unique().tolist())
#Створюємо змінну, яка зберігає обрану частину світу
continent_choice = st.sidebar.radio(
    "Оберіть частину світу:",
    options=continent_list
)

st.sidebar.markdown("---")
st.sidebar.subheader("Фільтр для Економіки")
eu_filter = st.sidebar.radio(
    "Членство в ЄС:",
    options=["Всі країни", "Тільки країни ЄС", "Країни поза ЄС"]
)

#Створення двох вкладок за допомогою st.tabs
tab1, tab2, tab3 = st.tabs([":bar_chart: Огляд та аналітика", ":clipboard: Деталі та фільтрація", ":chart_with_upwards_trend: Економічний аналіз (2.6+)"])

#Наповнюємо першу вкладку
with tab1:
    st.subheader("Огляд даних та часова шкала")
    
    st.write("Натисніть кнопку нижче, щоб оглянути датасет:")
    
    # Ініціалізуємо змінну в пам'яті, якщо її ще немає
    if 'show_df_clicked' not in st.session_state:
        st.session_state.show_df_clicked = False

    # Якщо кнопку натиснули — запам'ятовуємо True у пам'ять
    if st.button("Показати весь датафрейм"):
        st.session_state.show_df_clicked = True

    # Перевіряємо значення з пам'яті 
    if st.session_state.show_df_clicked:
        min_year = int(df['End Year Clean'].min())
        max_year = int(df['End Year Clean'].max())

        # створюємо повзунок-слайдер
        selected_years = st.slider(
            "Фільтр по роках закінчення будівництва (End Year):",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1
        )

        # Фільтруємо таблицю
        filtered_by_year = df[
            (df['End Year Clean'] >= selected_years[0]) & 
            (df['End Year Clean'] <= selected_years[1])
        ]

        # Виводимо кількість та саму таблицю
        st.write(f"Знайдено записів: **{len(filtered_by_year)}**")
        st.dataframe(filtered_by_year, use_container_width=True)

    #Розділяємо візуально блоки лінією
    st.markdown("---")
    
    # Кругова діаграма по середовищу розташування (міські / міжміські)
    st.subheader("Розподіл залізниць за середовищем розташування")

    #Рахуємо кількість проєктів для кожного середовища
    env_counts = df['Environment_Clean'].value_counts().reset_index()
    env_counts.columns = ['Середовище', 'Кількість']
    
    # Локалізація підписів
    env_counts['Середовище'] = env_counts['Середовище'].map({
        'Urban': 'Міські (Urban)',
        'Suburban': 'Міжміські / Приміські (Suburban)'
    }).fillna(env_counts['Середовище'])

    #Будуємо кругову діаграму
    fig = px.pie(
        env_counts, 
        values='Кількість', 
        names='Середовище', 
        hole=0.3, #робимо виріз у центрі
        color_discrete_sequence=['#2b5c8f', '#e67e22']
    )
    #розміщуємо текстові підписи з відсотками прямо всередині секторів діаграми
    fig.update_traces(textposition='inside', textinfo='percent+label')
    #Відображаємо графік у вікні браузера
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Діаграма демонструє співвідношення міських та приміських/міжміських рейкових проєктів.")


#Наповнюємо другу вкладку
with tab2:
    st.subheader("Відфільтровані залізниці")
    
    filtered_tab2 = df.copy()

    # Фільтрація за частиною світу
    if continent_choice != "Всі регіони":
        filtered_tab2 = filtered_tab2[filtered_tab2['Continent'] == continent_choice]
        
    # Фільтрація за кількістю станцій
    if station_choice == "1 - 10":
        filtered_tab2 = filtered_tab2[(filtered_tab2['Number of Stations'] >= 1) & (filtered_tab2['Number of Stations'] <= 10)]
    elif station_choice == "11 - 30":
        filtered_tab2 = filtered_tab2[(filtered_tab2['Number of Stations'] >= 11) & (filtered_tab2['Number of Stations'] <= 30)]
    elif station_choice == "31 - ...":
        filtered_tab2 = filtered_tab2[filtered_tab2['Number of Stations'] >= 31]

    #Формуємо  таблицю з 4 обов'язкових колонок з одиницями вимірювання
    display_df = pd.DataFrame({
        "Назва залізниці": filtered_tab2['Line name'].fillna(filtered_tab2['Project title']),
        "Країна та місто": filtered_tab2['Country'] + ", " + filtered_tab2['City'],
        "Протяжність (милі / miles)": filtered_tab2['Length (Miles)'],
        "Вартість (млн GBP / mil GBP)": filtered_tab2['Converted to mil GBP']
    })
    
    st.write(f"Знайдено об'єктів за обраними критеріями: **{len(display_df)}**")
    
    st.dataframe(
        display_df, 
        use_container_width=True,
        hide_index=True
    )

#Наповнюємо третю вкладку
with tab3:
    st.header("Аналіз макроекономічних показників країн світу (2022)")
    st.write("Інтерактивний дашборд за матеріалами дослідження")
    
    #Застосування фільтра 
    econ_filtered = df_econ.copy()
    if eu_filter == "Тільки країни ЄС":
        econ_filtered = econ_filtered[econ_filtered['EU member'] == 'Країна ЄС']
    elif eu_filter == "Країни поза ЄС":
        econ_filtered = econ_filtered[econ_filtered['EU member'] == 'Не в ЄС']
        
    # Можливість ознайомитися з повним датасетом
    with st.expander(":mag: Натисніть, щоб оглянути весь датасет 2.6"):
        st.write(f"Знайдено країн: **{len(econ_filtered)}**")
        st.dataframe(econ_filtered, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # Графіки у дві колонки
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ВВП та очікувана тривалість життя")
        fig_scatter = px.scatter(
            econ_filtered,
            x="GDP per capita",
            y="Life expectancy",
            color="EU member",
            hover_name="Country Name",
            log_x=True,
            title="Залежність тривалості життя від ВВП (шкала Log)",
            labels={"GDP per capita": "ВВП на душу населення (USD)", "Life expectancy": "Тривалість життя (років)", "EU member": "Статус ЄС"},
            color_discrete_map={'Країна ЄС': '#2ecc71', 'Не в ЄС': '#3498db'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.info("**Висновок:** Вищий рівень ВВП безпосередньо корелює з більшою тривалістю життя. Країни ЄС стабільно тримаються на рівні 78–83 років.")

    with col2:
        st.subheader("Проникнення інтернету vs ВВП")
        fig_net = px.scatter(
            econ_filtered,
            x="Internet users",
            y="GDP per capita",
            color="EU member",
            hover_name="Country Name",
            log_y=True,
            title="Рівень цифровізації населення vs ВВП",
            labels={"Internet users": "Користувачі інтернету (% населення)", "GDP per capita": "ВВП на душу населення (USD)", "EU member": "Статус ЄС"},
            color_discrete_map={'Країна ЄС': '#e74c3c', 'Не в ЄС': '#9b59b6'}
        )
        st.plotly_chart(fig_net, use_container_width=True)
        st.info("**Висновок:** Усі розвинені економіки мають показник проникнення інтернету вище 85%. Низький рівень цифровізації характерний для країн із низьким ВВП.")
        
    st.markdown("---")
    
    #порівняння окремих країн
    st.subheader("Порівняння окремих країн за рівнем інфляції / безробіття")
    all_countries = sorted(econ_filtered['Country Name'].unique().tolist())
    default_countries = [c for c in ['Ukraine', 'Poland', 'Germany', 'United States', 'France'] if c in all_countries]
    
    selected_countries = st.multiselect(
        "Оберіть країни для порівняння:",
        options=all_countries,
        default=default_countries
    )
    
    if selected_countries:
        bar_data = econ_filtered[econ_filtered['Country Name'].isin(selected_countries)]
        chosen_metric = st.selectbox("Оберіть показник:", ["Inflation", "Unemployment"])
        metric_name = "Рівень інфляції (%)" if chosen_metric == "Inflation" else "Рівень безробіття (%)"
        
        fig_bar = px.bar(
            bar_data,
            x="Country Name",
            y=chosen_metric,
            color="EU member",
            title=f"Порівняння показника: {metric_name}",
            labels={"Country Name": "Країна", chosen_metric: metric_name},
            text_auto='.1f'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.info("**Висновок:** Інтерактивна діаграма наочно демонструє вплив кризи 2022 року на інфляційні та соціальні показники обраних держав.")