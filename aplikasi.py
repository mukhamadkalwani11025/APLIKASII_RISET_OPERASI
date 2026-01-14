import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==================================================
# FORWARD RECURSION - DYNAMIC PROGRAMMING
# ==================================================
def forward_recursion(data, stok_awal, kapasitas, kirim_sedikit,
                      kirim_banyak, biaya_sedikit, biaya_banyak, biaya_simpan):

    dp = {}
    keputusan = {}

    dp[0] = {stok_awal: 0}
    keputusan[0] = {}

    # Forward Recursion (Bottom-Up)
    for hari in range(1, len(data) + 1):
        dp[hari] = {}
        keputusan[hari] = {}

        kebutuhan = data.loc[hari - 1, 'Kebutuhan']

        for stok_lama, biaya_lama in dp[hari - 1].items():
            for aksi, jumlah_kirim, biaya_kirim in [
                ("Sedikit", kirim_sedikit, biaya_sedikit),
                ("Banyak", kirim_banyak, biaya_banyak)
            ]:
                stok_baru = stok_lama + jumlah_kirim - kebutuhan

                if 0 <= stok_baru <= kapasitas:
                    biaya_total = biaya_lama + biaya_kirim + stok_baru * biaya_simpan

                    if stok_baru not in dp[hari] or biaya_total < dp[hari][stok_baru]:
                        dp[hari][stok_baru] = biaya_total
                        keputusan[hari][stok_baru] = (stok_lama, aksi)

    stok_akhir = min(dp[len(data)], key=dp[len(data)].get)
    biaya_min = dp[len(data)][stok_akhir]

    # Traceback
    jadwal = []
    stok = stok_akhir

    for hari in range(len(data), 0, -1):
        stok_prev, aksi = keputusan[hari][stok]
        biaya_kirim = biaya_sedikit if aksi == "Sedikit" else biaya_banyak
        biaya_hari = biaya_kirim + stok * biaya_simpan
        jadwal.append((hari, aksi, stok, biaya_hari))
        stok = stok_prev

    jadwal.reverse()
    return jadwal, biaya_min


# ==================================================
# GUI
# ==================================================
root = tk.Tk()
root.title("APLIKASI PENJADWALAN KIRIM BANTUAN")
root.geometry("1000x700")
root.configure(bg="#F5F5F5")

# ================== FRAME INPUT ==================
frame_input = ttk.LabelFrame(root, text="Input Data")
frame_input.pack(fill="x", padx=15, pady=10)

inputs = {
    "Stok Awal": 5000,
    "Kapasitas Gudang": 15000,
    "Kirim Sedikit": 3000,
    "Kirim Banyak": 6000,
    "Biaya Kirim Sedikit": 2000000,
    "Biaya Kirim Banyak": 3500000,
    "Biaya Simpan per Paket": 2000
}

entries = {}
row = 0
for label, val in inputs.items():
    ttk.Label(frame_input, text=label).grid(row=row, column=0, sticky="w", pady=4)
    ent = ttk.Entry(frame_input, width=25)
    ent.insert(0, val)
    ent.grid(row=row, column=1, pady=4)
    entries[label] = ent
    row += 1


# ================== FRAME BUTTON ==================
frame_button = tk.Frame(root, bg="#F5F5F5")
frame_button.pack(pady=10)

hasil_jadwal_global = None
data_global = None

# ================== OUTPUT ==================
frame_output = ttk.LabelFrame(root, text="Hasil Penjadwalan Optimal")
frame_output.pack(fill="both", expand=True, padx=15, pady=10)

text = tk.Text(frame_output, height=18, font=("Consolas", 10))
text.pack(fill="both", expand=True)


# ================== PROSES ==================
def proses():
    global hasil_jadwal_global, data_global
    try:
        data = pd.read_csv("dataset_banjir_aceh.csv")

        jadwal, biaya_total = forward_recursion(
            data,
            int(entries["Stok Awal"].get()),
            int(entries["Kapasitas Gudang"].get()),
            int(entries["Kirim Sedikit"].get()),
            int(entries["Kirim Banyak"].get()),
            int(entries["Biaya Kirim Sedikit"].get()),
            int(entries["Biaya Kirim Banyak"].get()),
            int(entries["Biaya Simpan per Paket"].get())
        )

        hasil_jadwal_global = jadwal
        data_global = data

        text.delete("1.0", tk.END)
        text.insert(tk.END, "HASIL PENJADWALAN OPTIMAL\n\nRincian Harian:\n\n")

        stok_list, biaya_list = [], []

        for h, aksi, stok, biaya in jadwal:
            text.insert(
                tk.END,
                f"Hari {h}: Kirim {aksi:<8} | Stok Akhir = {stok:<6} | "
                f"Biaya Hari Ini = Rp {biaya:,}\n"
            )
            stok_list.append(stok)
            biaya_list.append(biaya)

        text.insert(tk.END, f"\nTOTAL BIAYA MINIMUM : Rp {biaya_total:,}")

        btn_export.config(state="normal")

        # Grafik
        plt.figure(figsize=(10,5))
        plt.plot(data['Hari'], data['Kebutuhan'], marker='o', label="Kebutuhan Warga")
        plt.plot(data['Hari'], stok_list, marker='o', label="Stok Akhir Gudang")
        plt.title("Kebutuhan dan Stok")
        plt.xlabel("Hari")
        plt.ylabel("Jumlah Paket Bantuan")
        plt.legend()
        plt.grid(True)
        plt.show()

        plt.figure(figsize=(10,5))
        plt.plot(data['Hari'], biaya_list, marker='o', color='red')
        plt.title("Biaya Distribusi per Hari")
        plt.xlabel("Hari")
        plt.ylabel("Biaya (Rp)")
        plt.grid(True)
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ================== EXPORT EXCEL ==================
def export_excel():
    if hasil_jadwal_global is None:
        return

    rows = []
    for h, aksi, stok, biaya in hasil_jadwal_global:
        rows.append({
            "Hari": h,
            "Keputusan Pengiriman": aksi,
            "Stok Akhir": stok,
            "Biaya Harian": biaya
        })

    df = pd.DataFrame(rows)
    os.makedirs("output", exist_ok=True)
    filename = "output/hasil_penjadwalan_simbantu.xlsx"
    df.to_excel(filename, index=False)

    messagebox.showinfo("Sukses", f"Data berhasil diexport ke:\n{filename}")


# ================== BUTTON ==================
btn_proses = tk.Button(
    frame_button, text="🔄 Proses Penjadwalan",
    bg="#1976D2", fg="white",
    font=("Segoe UI", 10, "bold"),
    width=25, command=proses
)
btn_proses.grid(row=0, column=0, padx=10)

btn_export = tk.Button(
    frame_button, text="📁 Export ke Excel",
    bg="#388E3C", fg="white",
    font=("Segoe UI", 10, "bold"),
    width=25, state="disabled",
    command=export_excel
)
btn_export.grid(row=0, column=1, padx=10)

root.mainloop()
