from bpmn_mp.dispatcher import dispatch_parse

# Lokasi file sample BPMN
CURRENT_DIR = Path(_file_).parent
BPMN_FILE = CURRENT_DIR / "samples" / "MyDiagram1.bpmn"
OUTPUT_FILE = CURRENT_DIR / "samples" / "output_Dispatcher.json"

def test_dispatch_bpmn_and_save_output():
    """
    Memastikan dispatch_parse dapat memproses file BPMN,
    mengembalikan data yang valid, dan menyimpan output.
    """
    try:
        # Jalankan fungsi dispatcher dengan file BPMN asli
        result, result_type = dispatch_parse(BPMN_FILE)

        # Simpan hasil ke file output
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Output disimpan di: {OUTPUT_FILE}")

    except Exception as e:
        print("Terjadi error saat menjalankan pengujian:")
        print(e)
        assert False, str(e)