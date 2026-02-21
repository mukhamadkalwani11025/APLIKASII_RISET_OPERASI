import streamlit as st
import pandas as pd

st.title("Aplikasi Optimasi Pengiriman Bantuan")
st.write("Algoritma Forward Recursion")

uploaded_file = st.file_uploader("Upload File CSV", type=["csv"])

if uploaded_file is not None:

    data = pd.read_csv(uploaded_file)

    st.subheader("Data yang Diinput")
    st.dataframe(data)

    # ===============================
    # Input Tambahan
    # ===============================
    stok_awal = st.number_input("Masukkan Stok Awal (S0)", min_value=0)
    max_stok = st.number_input("Batas Maksimum Stok Gudang", min_value=0, value=100)
    max_backorder = st.number_input("Batas Maksimal Backorder", min_value=0, value=20)

    if st.button("Hitung Optimasi"):

        st.info("Menjalankan Forward Recursion...")

        # ===============================
        # 1. Ambil Data dari CSV
        # ===============================
        permintaan = data["Permintaan"].tolist()
        biaya_kirim = data["BiayaKirim"].tolist()
        biaya_simpan = data["BiayaSimpan"].tolist()
        biaya_tetap = data["BiayaTetap"].tolist()
        biaya_denda = data["BiayaDenda"].tolist()
        kapasitas_kirim = data["KapasitasKirim"].tolist()

        jumlah_hari = len(permintaan)

        # Range stok bisa negatif (backorder)
        range_stok = range(-max_backorder, max_stok + 1)

        # ===============================
        # 2. Inisialisasi DP
        # ===============================
        Biaya = {}
        Keputusan = {}

        for s in range_stok:
            for t in range(jumlah_hari + 1):
                Biaya[(s, t)] = float('inf')
                Keputusan[(s, t)] = 0

        Biaya[(stok_awal, 0)] = 0

        # ===============================
        # 3. Forward Recursion
        # ===============================
        for t in range(1, jumlah_hari + 1):

            for s in range_stok:

                if Biaya[(s, t-1)] != float('inf'):

                    for x in range(0, kapasitas_kirim[t-1] + 1):

                        stok_baru = s + x - permintaan[t-1]

                        if -max_backorder <= stok_baru <= max_stok:

                            total_biaya = Biaya[(s, t-1)]

                            # Biaya kirim
                            if x > 0:
                                total_biaya += biaya_tetap[t-1]
                                total_biaya += x * biaya_kirim[t-1]

                            # Biaya simpan
                            if stok_baru > 0:
                                total_biaya += stok_baru * biaya_simpan[t-1]

                            # Biaya denda (backorder)
                            if stok_baru < 0:
                                total_biaya += abs(stok_baru) * biaya_denda[t-1]

                            # Simpan biaya minimum
                            if total_biaya < Biaya[(stok_baru, t)]:
                                Biaya[(stok_baru, t)] = total_biaya
                                Keputusan[(stok_baru, t)] = x

        # ===============================
        # 4. Ambil Biaya Minimum
        # ===============================
        total_biaya_minimum = float('inf')
        stok_optimal = 0

        for s in range_stok:
            if Biaya[(s, jumlah_hari)] < total_biaya_minimum:
                total_biaya_minimum = Biaya[(s, jumlah_hari)]
                stok_optimal = s

        # ===============================
        # 5. Backtracking
        # ===============================
        st.info("Menjalankan Backtracking...")

        jadwal = [0] * jumlah_hari
        stok_harian = [0] * (jumlah_hari + 1)

        stok_harian[jumlah_hari] = stok_optimal

        for t in range(jumlah_hari, 0, -1):
            kirim = Keputusan[(stok_optimal, t)]
            jadwal[t-1] = kirim
            stok_optimal = stok_optimal - kirim + permintaan[t-1]
            stok_harian[t-1] = stok_optimal

        # ===============================
        # 6. Tampilkan Hasil
        # ===============================
        st.success("Proses Selesai!")

        hasil_df = pd.DataFrame({
            "Hari": list(range(1, jumlah_hari + 1)),
            "Permintaan": permintaan,
            "Jumlah Dikirim": jadwal,
            "Stok Akhir Hari": stok_harian[1:]
        })

        st.subheader("Jadwal Pengiriman Optimal")
        st.dataframe(hasil_df)

        st.subheader("Total Biaya Minimum")
        st.success(f"Rp {total_biaya_minimum:,.0f}")

        # ===============================
        # 7. VISUALISASI
        # ===============================

        st.subheader("Visualisasi Hasil Optimasi")

        # Grafik Stok per Hari
        st.markdown("### 📊 Grafik Stok per Hari")
        stok_df = pd.DataFrame({
            "Hari": list(range(1, jumlah_hari + 1)),
            "Stok": stok_harian[1:]
        })
        st.line_chart(stok_df.set_index("Hari"))

        # Grafik Jumlah Pengiriman per Hari
        st.markdown("### 📦 Grafik Jumlah Pengiriman per Hari")
        kirim_df = pd.DataFrame({
            "Hari": list(range(1, jumlah_hari + 1)),
            "Jumlah Dikirim": jadwal
        })
        st.bar_chart(kirim_df.set_index("Hari"))

        # Grafik Perbandingan Permintaan dan Pengiriman
        st.markdown("### 📈 Grafik Perbandingan Permintaan vs Pengiriman")
        perbandingan_df = pd.DataFrame({
            "Hari": list(range(1, jumlah_hari + 1)),
            "Permintaan": permintaan,
            "Jumlah Dikirim": jadwal
        })
        st.line_chart(perbandingan_df.set_index("Hari"))

        # Ringkasan Total Biaya
        st.markdown("### 💰 Ringkasan Total Biaya")
        st.metric(
            label="Total Biaya Minimum",
            value=f"Rp {total_biaya_minimum:,.0f}"
        )
