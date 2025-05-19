import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

# Konfigurasi halaman
st.set_page_config(page_title="Hasil Panen Tanaman", page_icon="🌾")
st.title('🌱 Aplikasi SAW Hasil Panen Tanaman 🌱')

# Informasi anggota
col1, col2 = st.columns(2)
with col1:
    st.write("Melania Intan Sagita")
    st.write("Fadiah Nur Sabiyyah")
with col2:
    st.write("123230005")
    st.write("123230006")

# Deskripsi
st.subheader("Deskripsi 📜")
st.write("Dataset ini adalah tentang hasil panen tanaman (crop yield) berdasarkan berbagai faktor agrikultur dan cuaca.")

# Load dataset
df = pd.read_csv("Projek/crop_yield.csv")

# Kriteria dan bobot default
default_criteria = {
    'Rainfall_mm': {'is_benefit': True, 'weight': 0.15},
    'Temperature_Celsius': {'is_benefit': True, 'weight': 0.15},
    'Fertilizer_Used': {'is_benefit': True, 'weight': 0.10},
    'Irrigation_Used': {'is_benefit': True, 'weight': 0.10},
    'Days_to_Harvest': {'is_benefit': False, 'weight': 0.20},
    'Yield_tons_per_hectare': {'is_benefit': True, 'weight': 0.30},
}

if 'criteria_config' not in st.session_state:
    st.session_state.criteria_config = default_criteria.copy()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dataset", "Grafik", "Cari Data", "Input Data", "Hasil Akhir"])

# Tab 1
with tab1:
    st.subheader("🗂️ Informasi Dataset")
    jmlh = st.number_input('Jumlah data yang ingin ditampilkan', 0, len(df), 100)
    st.dataframe(df.head(jmlh))

    st.write(' Dimensi Dataset:', df.shape)
    st.subheader('Statistik Deskriptif:')
    st.write(df.describe())
    st.subheader('Nilai Kosong:')
    st.write(df.isnull().sum())

# Tab 2
with tab2:
    st.subheader("📊 Grafik dari Data Asli")
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    selected_col = st.selectbox("Pilih kolom numerik untuk digrafikkan", numeric_cols)

    avg_by_crop = df.groupby('Crop')[selected_col].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    avg_by_crop.plot(kind='bar', ax=ax, color='lightgreen', edgecolor='black')
    ax.set_title(f"Rata-rata {selected_col} per Tanaman")
    ax.set_ylabel(selected_col)
    ax.set_xlabel("Tanaman")
    st.pyplot(fig)

# Tab 3
with tab3:
    st.subheader("🔍 Cari Data")
    st.write("Cari Data Berdasarkan Tanaman, Wilayah, dan Jenis Tanah")

    crop_options = ['All'] + sorted(df['Crop'].unique().tolist())
    region_options = ['All'] + sorted(df['Region'].unique().tolist())
    soil_options = ['All'] + sorted(df['Soil_Type'].unique().tolist())

    selected_crop = st.selectbox('Pilih Tanaman (Crop)', crop_options)
    selected_region = st.selectbox('Pilih Wilayah (Region)', region_options)
    selected_soil = st.selectbox('Pilih Jenis Tanah (Soil Type)', soil_options)

    filtered = df.copy()
    if selected_crop != 'All':
        filtered = filtered[filtered['Crop'] == selected_crop]
    if selected_region != 'All':
        filtered = filtered[filtered['Region'] == selected_region]
    if selected_soil != 'All':
        filtered = filtered[filtered['Soil_Type'] == selected_soil]

    st.write(f"Menampilkan {len(filtered)} data")
    st.dataframe(filtered)

# Tab 4
with tab4:
    st.subheader("✒️ Input Data")
    st.write("Yuk bantu Lucas cari tanaman yang nggak drama, cuma butuh air dan cinta 💧❤️")
    st.markdown("Atur bobot dan jenis kriteria (Benefit / Cost). Total bobot harus = 1.0 yaa!")
    st.image("Projek/Lucas.jpg", width=200)


    updated_criteria = {}
    total_weight = 0

    for k in default_criteria:
        st.markdown(f"#### {k}")
        col1, col2 = st.columns(2)
        with col1:
            is_benefit = st.radio(f"Tipe {k}", ["Benefit", "Cost"],
                                  index=0 if default_criteria[k]['is_benefit'] else 1,
                                  key=f"type_{k}")
            is_benefit_bool = is_benefit == "Benefit"
        with col2:
            weight = st.number_input(f"Bobot {k}", 0.0, 1.0, default_criteria[k]['weight'], 0.01, key=f"weight_{k}")
            total_weight += weight
        updated_criteria[k] = {'is_benefit': is_benefit_bool, 'weight': weight}

    if abs(total_weight - 1.0) > 0.001:
        st.warning("⚠ Total bobot harus sama dengan 1.0. Sekarang: {:.2f}".format(total_weight))
    else:
        st.success("✅ Total bobot valid!")
        st.session_state.criteria_config = updated_criteria
        st.info("Klik tab Hasil Akhir untuk melihat hasil SAW.")

# Tab 5
with tab5:
    st.subheader("📋 Hasil Akhir")

    # Ambil kriteria dan bobot
    criteria = [(k, v['is_benefit']) for k, v in st.session_state.criteria_config.items()]
    weights = {k: v['weight'] for k, v in st.session_state.criteria_config.items()}

    # Encode dan konversi data
    df_encoded = df.copy()
    for col in ['Region', 'Soil_Type', 'Crop', 'Weather_Condition']:
        df_encoded[col] = LabelEncoder().fit_transform(df_encoded[col])
    df_encoded['Fertilizer_Used'] = df_encoded['Fertilizer_Used'].astype(int)
    df_encoded['Irrigation_Used'] = df_encoded['Irrigation_Used'].astype(int)

    data_saw = df_encoded[[col for col, _ in criteria]]
    normalized = data_saw.copy()

    for col, is_benefit in criteria:
        if is_benefit:
            normalized[col] = data_saw[col] / data_saw[col].max()
        else:
            normalized[col] = data_saw[col].min() / data_saw[col]

    normalized['SAW_Score'] = sum(normalized[col] * weights[col] for col, _ in criteria)

    df_result = df.copy()
    df_result['SAW_Score'] = normalized['SAW_Score']
    df_result['Ranking'] = df_result['SAW_Score'].rank(ascending=False, method='min')
    df_sorted = df_result.sort_values(by='SAW_Score', ascending=False)

    st.markdown("### Konfigurasi Kriteria dan Bobot")
    st.dataframe(pd.DataFrame({
        'Kriteria': [k for k, _ in criteria],
        'Tipe': ['Benefit' if b else 'Cost' for _, b in criteria],
        'Bobot': [weights[k] for k, _ in criteria]
    }))

    st.markdown("### Top 10 Tanaman Berdasarkan Skor SAW")
    st.dataframe(df_sorted[['Crop', 'Region', 'Soil_Type', 'Yield_tons_per_hectare', 'SAW_Score', 'Ranking']].head(10))

    avg_tanam = df_result.groupby('Crop')['Days_to_Harvest'].mean().sort_values()

    # Kesimpulan
    st.subheader("🧐 Kesimpulan")
    top_crop = df_sorted.iloc[0]['Crop']
    cepat_tanam = avg_tanam.index[0]
    cepat_tanam_days = avg_tanam.min()
    # Cari kriteria dengan bobot terbesar
    kriteria_terpenting = max(weights, key=weights.get)
    bobot_terbesar = weights[kriteria_terpenting]


    st.markdown(f"""
    - 🏆 Tanaman dengan skor SAW tertinggi: *{top_crop}*
    - 🕰️ Tanaman tercepat waktu panen rata-rata: *{cepat_tanam}* ({cepat_tanam_days:.1f} hari)
    - 📌 Kriteria terpenting : *{kriteria_terpenting}* (bobot {bobot_terbesar:.2f})
    - ✅ Aplikasi ini membantu memilih tanaman terbaik berdasarkan data aktual.
    """)