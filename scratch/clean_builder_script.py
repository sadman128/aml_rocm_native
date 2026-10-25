import re

file_path = "scratch/build_v10_final_notebook.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remove reference dirs from CONFIG
code = code.replace('    "v10_multy_reference_dir"     : "outputs/v10_multy_class",\n', '')
code = code.replace('    "v10_reference_dir"           : "outputs/v10",\n', '')

# 2. Clean Cell 04
old_c4_check = '''if len(csv_files) == 0:
    # If raw data files are absent, check if preprocessed parquet exists in reference dirs
    ref_clean = Path(CONFIG.get("v10_multy_reference_dir", "outputs/v10_multy_class")) / "artifacts" / "data_clean.parquet"
    if not ref_clean.exists():
        ref_clean = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "data_clean.parquet"
    if not ref_clean.exists():
        raise FileNotFoundError(f"No CSV/Parquet files found in {DATA_DIR} and no cached clean parquet available.")
    print(f"  [REUSE] Raw CSVs absent, but verified clean data exists at {ref_clean}")'''

new_c4_check = '''if len(csv_files) == 0:
    ref_clean = ARTIFACT_DIR / "data_clean.parquet"
    if not ref_clean.exists():
        raise FileNotFoundError(f"No CSV/Parquet files found in {DATA_DIR} and no cached clean parquet available.")
    print(f"  [CACHE] Clean dataset available at {ref_clean}")'''
assert old_c4_check in code, "Failed to find old_c4_check"
code = code.replace(old_c4_check, new_c4_check)

# 3. Clean Cell 05
old_c5 = '''# Check for existing verified artifacts from v10_multy_class or v10
for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_pq = Path(CONFIG.get(ref_key, "")) / "artifacts" / "raw_data.parquet"
    ref_meta = Path(CONFIG.get(ref_key, "")) / "artifacts" / "raw_data_meta.json"
    if not pq_path.exists() and ref_pq.exists() and ref_meta.exists():
        print(f"[REUSE] Fast startup: Reusing verified raw data from {ref_pq}...")
        shutil.copy2(ref_pq, pq_path)
        shutil.copy2(ref_meta, raw_meta)
        SM.mark_done("raw_loading")
        break'''
assert old_c5 in code, "Failed to find old_c5"
code = code.replace(old_c5, "# Loading raw data from disk cache if present")

# 4. Clean Cell 06
old_c6 = '''for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_clean = Path(CONFIG.get(ref_key, "")) / "artifacts" / "data_clean.parquet"
    ref_meta  = Path(CONFIG.get(ref_key, "")) / "artifacts" / "data_clean_meta.json"
    if not clean_path.exists() and ref_clean.exists() and ref_meta.exists():
        print(f"[REUSE] Fast startup: Reusing cleaned dataset from {ref_clean}...")
        shutil.copy2(ref_clean, clean_path)
        shutil.copy2(ref_meta, clean_meta)
        SM.mark_done("cleaning")
        break'''
assert old_c6 in code, "Failed to find old_c6"
code = code.replace(old_c6, "# Loading cleaned dataset from disk cache if present")

# 5. Clean Cell 08
old_c8 = '''for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_split = Path(CONFIG.get(ref_key, "")) / "artifacts" / "train_test_split.npz"
    if not split_path.exists() and ref_split.exists():
        print(f"[REUSE] Fast startup: Reusing train/test split from {ref_split}...")
        shutil.copy2(ref_split, split_path)
        SM.mark_done("train_test_split")
        break'''
assert old_c8 in code, "Failed to find old_c8"
code = code.replace(old_c8, "# Loading train/test split from disk cache if present")

# 6. Clean Cell 09
old_c9 = '''for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_dev = Path(CONFIG.get(ref_key, "")) / "artifacts" / "dev_split.npz"
    if not dev_path.exists() and ref_dev.exists():
        print(f"[REUSE] Fast startup: Reusing dev split from {ref_dev}...")
        shutil.copy2(ref_dev, dev_path)
        SM.mark_done("dev_split")
        break'''
assert old_c9 in code, "Failed to find old_c9"
code = code.replace(old_c9, "# Loading dev split from disk cache if present")

# 7. Clean Cell 10
old_c10 = '''for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_enc = Path(CONFIG.get(ref_key, "")) / "artifacts" / "encoded.npz"
    if not enc_path.exists() and ref_enc.exists():
        print(f"[REUSE] Fast startup: Reusing encoded matrices from {ref_enc}...")
        shutil.copy2(ref_enc, enc_path)
        SM.mark_done("encoding")
        break'''
assert old_c10 in code, "Failed to find old_c10"
code = code.replace(old_c10, "# Loading encoded features from disk cache if present")

# 8. Clean Cell 11
old_c11 = '''for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_mi     = Path(CONFIG.get(ref_key, "")) / "artifacts" / "mi_features.json"
    ref_mi_idx = Path(CONFIG.get(ref_key, "")) / "artifacts" / "mi_indices.npz"
    if not mi_path.exists() and ref_mi.exists() and ref_mi_idx.exists():
        print(f"[REUSE] Fast startup: Reusing Top-40 MI features from {ref_mi}...")
        shutil.copy2(ref_mi, mi_path)
        shutil.copy2(ref_mi_idx, mi_idx_path)
        SM.mark_done("mi_selection")
        break'''
assert old_c11 in code, "Failed to find old_c11"
code = code.replace(old_c11, "# Loading MI features from disk cache if present")

# 9. Clean Cell 12
old_c12 = '''for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_scale = Path(CONFIG.get(ref_key, "")) / "artifacts" / "scaled.npz"
    if not scale_path.exists() and ref_scale.exists():
        print(f"[REUSE] Fast startup: Reusing scaled matrices from {ref_scale}...")
        shutil.copy2(ref_scale, scale_path)
        SM.mark_done("scaling")
        break'''
assert old_c12 in code, "Failed to find old_c12"
code = code.replace(old_c12, "# Loading scaled matrices from disk cache if present")

# 10. Clean Cell 14
old_c14 = '''for ref_key in ["v10_multy_reference_dir", "v10_reference_dir"]:
    ref_pfi     = Path(CONFIG.get(ref_key, "")) / "artifacts" / "pfi_features.json"
    ref_pfi_imp = Path(CONFIG.get(ref_key, "")) / "artifacts" / "pfi_importance.csv"
    if not pfi_path.exists() and ref_pfi.exists() and ref_pfi_imp.exists():
        print(f"[REUSE] Fast startup: Reusing Adversarial PFI features from {ref_pfi}...")
        shutil.copy2(ref_pfi, pfi_path)
        shutil.copy2(ref_pfi_imp, pfi_imp_path)
        SM.mark_done("pfi_selection")
        break'''
assert old_c14 in code, "Failed to find old_c14"
code = code.replace(old_c14, "# Loading Adversarial PFI features from disk cache if present")

# 11. Remove model shortcut in generate_seed_cell for Binary Defense
old_seed_bin = '''    v10_bin_dir = MODEL_DIR / "v10_binary_defense"
    if seed_SM.report("v10_binary_train") and (v10_bin_dir / "best.pt").exists():
        v10_bin_model = IDSNet(len(extension_idx_local), num_classes=2).to(DEVICE)
        v10_bin_model.load_state_dict(
            torch.load(v10_bin_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"]
        )
        print("  [LOAD] V10 Binary Defense loaded from checkpoint.")
    else:
        # Check if trained weights exist in reference multi-class run for fast resume
        ref_bin_ckpt = Path(CONFIG.get("v10_multy_reference_dir", "")) / "seeds" / str(RUN_SEED) / "models" / "v10_binary_defense" / "best.pt"
        if ref_bin_ckpt.exists():
            print(f"  [REUSE] Reusing pre-trained V10 binary weights from {{ref_bin_ckpt}}...")
            v10_bin_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ref_bin_ckpt, v10_bin_dir / "best.pt")
            v10_bin_model = IDSNet(len(extension_idx_local), num_classes=2).to(DEVICE)
            v10_bin_model.load_state_dict(torch.load(v10_bin_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
            seed_SM.mark_done("v10_binary_train")
        else:
            t_vb = time.perf_counter()
            v10_bin_model = IDSNet(len(extension_idx_local), num_classes=2)
            bw = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train_s).astype(np.float32)
            bw_t = torch.as_tensor(bw, dtype=torch.float32, device=DEVICE)
            
            # Phase 1: clean warm-up
            v10_bin_model, _ = train_with_resume(
                v10_bin_model, v10_bin_dir / "phase1_clean",
                X_train_ext_s, y_train_s,
                X_dev_ext_s, y_dev_s,
                CONFIG["v10_clean_epochs"], RUN_SEED + 20_000, "V10 Binary Phase1 Clean", CONFIG,
                custom_loss_weights=bw_t
            )
            # Phase 2: online PGD adversarial training
            v10_bin_model, hist_bin = train_online_pgd_with_resume(
                v10_bin_model, v10_bin_dir,
                X_train_ext_s, y_train_s,
                X_dev_ext_s, y_dev_s,
                CONFIG["v10_online_epochs"], RUN_SEED + 20_000, "V10 Binary Online PGD", CONFIG,
                ext_bounds, ext_mask, custom_loss_weights=bw_t
            )
            hist_bin.to_csv(v10_bin_dir / "history_online.csv", index=False)
            seed_SM.mark_done("v10_binary_train", {{"seconds": time.perf_counter() - t_vb}})
            print(f"  [OK] V10 Binary Defense trained in {{time.perf_counter()-t_vb:.1f}}s")'''

new_seed_bin = '''    v10_bin_dir = MODEL_DIR / "v10_binary_defense"
    if seed_SM.report("v10_binary_train") and (v10_bin_dir / "best.pt").exists():
        v10_bin_model = IDSNet(len(extension_idx_local), num_classes=2).to(DEVICE)
        v10_bin_model.load_state_dict(
            torch.load(v10_bin_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"]
        )
        print("  [LOAD] V10 Binary Defense loaded from checkpoint.")
    else:
        t_vb = time.perf_counter()
        v10_bin_model = IDSNet(len(extension_idx_local), num_classes=2)
        bw = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train_s).astype(np.float32)
        bw_t = torch.as_tensor(bw, dtype=torch.float32, device=DEVICE)
        
        # Phase 1: clean warm-up
        print(f"  [PHASE 1] Clean warm-up training for {{CONFIG['v10_clean_epochs']}} epochs...")
        v10_bin_model, _ = train_with_resume(
            v10_bin_model, v10_bin_dir / "phase1_clean",
            X_train_ext_s, y_train_s,
            X_dev_ext_s, y_dev_s,
            CONFIG["v10_clean_epochs"], RUN_SEED + 20_000, "V10 Binary Phase1 Clean", CONFIG,
            custom_loss_weights=bw_t
        )
        # Phase 2: online PGD adversarial training
        print(f"  [PHASE 2] Online PGD adversarial training for {{CONFIG['v10_online_epochs']}} epochs...")
        v10_bin_model, hist_bin = train_online_pgd_with_resume(
            v10_bin_model, v10_bin_dir,
            X_train_ext_s, y_train_s,
            X_dev_ext_s, y_dev_s,
            CONFIG["v10_online_epochs"], RUN_SEED + 20_000, "V10 Binary Online PGD", CONFIG,
            ext_bounds, ext_mask, custom_loss_weights=bw_t
        )
        hist_bin.to_csv(v10_bin_dir / "history_online.csv", index=False)
        seed_SM.mark_done("v10_binary_train", {{"seconds": time.perf_counter() - t_vb}})
        print(f"  [OK] V10 Binary Defense trained in {{time.perf_counter()-t_vb:.1f}}s")'''
assert old_seed_bin in code, "Failed to find old_seed_bin"
code = code.replace(old_seed_bin, new_seed_bin)

# 12. Remove model shortcut in generate_seed_cell for Attack Classifier
old_seed_atk = '''    atk_cls_dir = MODEL_DIR / "v10_attack_classifier"
    if seed_SM.report("v10_attack_cls_train") and (atk_cls_dir / "best.pt").exists():
        attack_model = IDSNet(len(extension_idx_local), num_classes=len(known_attacks)).to(DEVICE)
        attack_model.load_state_dict(
            torch.load(atk_cls_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"]
        )
        print("  [LOAD] Attack Classifier loaded from checkpoint.")
    else:
        ref_atk_ckpt = Path(CONFIG.get("v10_multy_reference_dir", "")) / "seeds" / str(RUN_SEED) / "models" / "v10_attack_classifier" / "best.pt"
        if ref_atk_ckpt.exists():
            print(f"  [REUSE] Reusing pre-trained Attack Classifier weights from {{ref_atk_ckpt}}...")
            atk_cls_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ref_atk_ckpt, atk_cls_dir / "best.pt")
            attack_model = IDSNet(len(extension_idx_local), num_classes=len(known_attacks)).to(DEVICE)
            attack_model.load_state_dict(torch.load(atk_cls_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
            seed_SM.mark_done("v10_attack_cls_train")
        else:
            t_va = time.perf_counter()
            attack_model = IDSNet(len(extension_idx_local), num_classes=len(known_attacks))
            
            classes_present = np.unique(y_tr_atk_local)
            aw = compute_class_weight("balanced", classes=classes_present, y=y_tr_atk_local).astype(np.float32)
            aw_full = np.ones(len(known_attacks), dtype=np.float32)
            for c, w in zip(classes_present, aw):
                aw_full[c] = w
            aw_t = torch.as_tensor(aw_full, dtype=torch.float32, device=DEVICE)
            
            attack_model, hist_atk = train_with_resume(
                attack_model, atk_cls_dir,
                X_tr_atk, y_tr_atk_local,
                X_dv_atk, y_dv_atk_local,
                CONFIG["attack_classifier_epochs"], RUN_SEED + 30_000, "V10 Attack Classifier", CONFIG,
                custom_loss_weights=aw_t
            )
            hist_atk.to_csv(atk_cls_dir / "history.csv", index=False)
            seed_SM.mark_done("v10_attack_cls_train", {{"seconds": time.perf_counter() - t_va}})
            print(f"  [OK] V10 Attack Classifier trained in {{time.perf_counter()-t_va:.1f}}s")'''

new_seed_atk = '''    atk_cls_dir = MODEL_DIR / "v10_attack_classifier"
    if seed_SM.report("v10_attack_cls_train") and (atk_cls_dir / "best.pt").exists():
        attack_model = IDSNet(len(extension_idx_local), num_classes=len(known_attacks)).to(DEVICE)
        attack_model.load_state_dict(
            torch.load(atk_cls_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"]
        )
        print("  [LOAD] Attack Classifier loaded from checkpoint.")
    else:
        t_va = time.perf_counter()
        attack_model = IDSNet(len(extension_idx_local), num_classes=len(known_attacks))
        
        classes_present = np.unique(y_tr_atk_local)
        aw = compute_class_weight("balanced", classes=classes_present, y=y_tr_atk_local).astype(np.float32)
        aw_full = np.ones(len(known_attacks), dtype=np.float32)
        for c, w in zip(classes_present, aw):
            aw_full[c] = w
        aw_t = torch.as_tensor(aw_full, dtype=torch.float32, device=DEVICE)
        
        print(f"  [TRAIN] Training known attack classifier for {{CONFIG['attack_classifier_epochs']}} epochs across {{len(known_attacks)}} classes...")
        attack_model, hist_atk = train_with_resume(
            attack_model, atk_cls_dir,
            X_tr_atk, y_tr_atk_local,
            X_dv_atk, y_dv_atk_local,
            CONFIG["attack_classifier_epochs"], RUN_SEED + 30_000, "V10 Attack Classifier", CONFIG,
            custom_loss_weights=aw_t
        )
        hist_atk.to_csv(atk_cls_dir / "history.csv", index=False)
        seed_SM.mark_done("v10_attack_cls_train", {{"seconds": time.perf_counter() - t_va}})
        print(f"  [OK] V10 Attack Classifier trained in {{time.perf_counter()-t_va:.1f}}s")'''
assert old_seed_atk in code, "Failed to find old_seed_atk"
code = code.replace(old_seed_atk, new_seed_atk)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Builder script cleaned and updated.")
