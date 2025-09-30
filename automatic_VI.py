import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Sentinel-2 Band Centers (nm)
s2_bands = {
    "Blue": 490,
    "Green": 560,
    "Red": 665,
    "NIR": 842
}

# Custom colors for each band
band_colors = {
    "Blue": 'lightblue',
    "Green": 'lightgreen',
    "Red": 'lightcoral',
    "NIR": 'orchid'
}

# Description for each band
band_descriptions = {
    "Blue": "absorption by pigments like anthocyanins and carotenoids",
    "Green": "reflection of green light due to low absorption",
    "Red": "strong absorption by chlorophyll",
    "NIR": "reflectance caused by leaf structure, not pigment"
}

def load_and_process_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
        df.columns = [col.strip().lower() for col in df.columns]

        if 'wavelength' not in df.columns or 'reflectance' not in df.columns:
            raise ValueError("CSV must contain 'wavelength' and 'reflectance' columns.")

        # Extract reflectance for Sentinel-2 bands
        band_reflectance = {}
        for name, center in s2_bands.items():
            closest_idx = (df['wavelength'] - center).abs().idxmin()
            band_reflectance[name] = df.loc[closest_idx, 'reflectance']

        # Generate custom index
        max_band = max(band_reflectance, key=band_reflectance.get)
        min_band = min(band_reflectance, key=band_reflectance.get)
        b1 = band_reflectance[max_band]
        b2 = band_reflectance[min_band]
        custom_index_diff = b1 - b2
        custom_index_ndiff = (b1 - b2) / (b1 + b2) if (b1 + b2) != 0 else 0

        # Create report
        report = "=== Sentinel-2 Band Reflectance ===\n"
        for band, refl in band_reflectance.items():
            report += f"{band} ({s2_bands[band]} nm): {refl:.4f}\n"

        report += "\n=== Automatic Custom Index ===\n"
        report += f"Max Reflectance: {max_band} = {b1:.4f}\n"
        report += f"Min Reflectance: {min_band} = {b2:.4f}\n"
        report += f"Custom Index (Diff): {custom_index_diff:.4f}\n"
        report += f"Custom Index (Normalized): {custom_index_ndiff:.4f}\n"

        report += "\n=== Scientific Reflectance Report ===\n"
        for band, refl in band_reflectance.items():
            level = "high" if refl > 0.5 else "medium" if refl > 0.2 else "low"
            report += f"- {band} ({s2_bands[band]} nm): Reflectance is {level} ({refl:.4f}) → typically indicates {band_descriptions[band]}.\n"

        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, report)

        # Plotting
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['wavelength'], df['reflectance'], label='Reflectance Spectrum', color='gray', linewidth=2)

        # Add shaded bands with custom colors
        band_width = 20  # nm width for visualization
        for band, center in s2_bands.items():
            ax.axvspan(center - band_width / 2, center + band_width / 2,
                       alpha=0.3, color=band_colors[band], label=f'{band} Band')

        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Reflectance')
        ax.set_title('Spectral Reflectance with Sentinel-2 Band Regions')
        ax.legend()
        ax.grid(True)

        # Clear previous plot (if any)
        for widget in plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create GUI window
root = tk.Tk()
root.title("Reflectance Analyzer - Sentinel-2")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

btn_load = tk.Button(frame, text="Load CSV and Analyze", command=load_and_process_csv)
btn_load.pack(pady=5)

plot_frame = tk.Frame(root)
plot_frame.pack()

text_box = tk.Text(root, height=20, width=100)
text_box.pack(padx=10, pady=10)

root.mainloop()
