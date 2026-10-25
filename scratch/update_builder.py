# scratch/update_builder.py
import re

builder_file = "scratch/build_v10_multiclass_notebook.py"
with open(builder_file, "r", encoding="utf-8") as f:
    code = f.read()

# Find where Cell 17 ends and Cell 18 begins
c17_end_marker = 'print("[OK] Hierarchical Decision Engine and Multiclass evaluation utilities initialized.")\'\'\')'
c21_start_marker = 'add_cell("code", \'\'\'# Cell 21 of 25 -- Aggregation of Multi-Seed Results (Mean +- Std)'

pos17 = code.find(c17_end_marker)
pos21 = code.find(c21_start_marker)

assert pos17 != -1, "Could not find c17_end_marker"
assert pos21 != -1, "Could not find c21_start_marker"

prefix = code[:pos17 + len(c17_end_marker)]
suffix = code[pos21:]

# Create clean seed cell generator
seed_generator_code = '''

    # -------------------------------------------------------------
    # Helper to generate unified, bug-free seed execution cells
    # -------------------------------------------------------------
    def generate_seed_cell(seed_num, cell_num):
        return f"""# Cell {cell_num:02d} of 25 -- SEED {seed_num} Execution (Full Training & Hierarchical Evaluation Suite)
RUN_SEED = {seed_num}
if RUN_SEED not in CONFIG["seeds"]:
    print(f"  [SKIP] Seed {{RUN_SEED}} skipped per CONFIG['seeds'].")
else:
    set_seed(RUN_SEED)
    t_seed_start = time.perf_counter()
    print(f"\\\\n======================================================================")
    print(f"  RUNNING SEED {{RUN_SEED}} -- HIERARCHICAL MULTICLASS V10 DEFENSE")
    print(f"======================================================================\\\\n")

    SEED_DIR   = OUTPUT_DIR / "seeds" / str(RUN_SEED)
    ATTACK_DIR = SEED_DIR / "attacks"
    MODEL_DIR  = SEED_DIR / "models"
    LOG_DIR    = SEED_DIR / "logs"
    for _d in [SEED_DIR, ATTACK_DIR, MODEL_DIR, LOG_DIR]:
        _d.mkdir(parents=True, exist_ok=True)

    atomic_save_json({{"seed": RUN_SEED, "status": "started", "start_time": time.time()}}, SEED_DIR / "seed_start.json")
    atomic_save_json(CONFIG, SEED_DIR / "config.json")
    seed_SM = StageManager(SEED_DIR)

    # -- Step A: Designate Random Held-Out Zero-Day Attack -----------------------
    rng_seed = np.random.RandomState(RUN_SEED)
    candidate_pool = MAJOR_ATTACK_FAMILIES if len(MAJOR_ATTACK_FAMILIES) > 0 else ATTACK_FAMILIES
    held_out_attack = rng_seed.choice(candidate_pool)
    known_attacks = [a for a in ATTACK_FAMILIES if a != held_out_attack]
    print(f"  [ZERO-DAY HELD-OUT] Excluded Attack Family: '{{held_out_attack}}'")
    print(f"  [KNOWN ATTACKS] {{len(known_attacks)}} attack families retained in training pool.")
    atomic_save_json({{"seed": RUN_SEED, "held_out_attack": held_out_attack, "known_attacks": known_attacks}},
                     SEED_DIR / "zero_day_spec.json")

    # Filter training/dev pools: completely drop the held-out attack from training
    train_keep_mask = (lbl_train_raw != held_out_attack)
    dev_keep_mask   = (lbl_dev_raw != held_out_attack)

    X_train_ext_s = X_train_ext[train_keep_mask]
    y_train_s     = y_train[train_keep_mask]
    lbl_train_s   = lbl_train_raw[train_keep_mask]

    X_dev_ext_s   = X_dev_ext[dev_keep_mask]
    y_dev_s       = y_dev[dev_keep_mask]
    lbl_dev_s     = lbl_dev_raw[dev_keep_mask]

    # Map labels in test set to Global IDs: Benign=0, known_attacks=1..K, held-out attack=OTHER_CLASS_ID
    y_test_global = np.zeros(len(lbl_test_raw), dtype=np.int64)
    for i, lbl in enumerate(lbl_test_raw):
        if lbl.lower() == "benign":
            y_test_global[i] = 0
        elif lbl == held_out_attack:
            y_test_global[i] = OTHER_CLASS_ID  # Ground truth label for held out is "Other"
        else:
            y_test_global[i] = ATTACK_TO_ID[lbl]

    print(f"  [DATA] Train pool: {{len(X_train_ext_s):,}} (held-out rows removed: {{(~train_keep_mask).sum():,}})")
    print(f"  [DATA] Test ground truth: Benign={{(y_test_global==0).sum():,}}, Known={{((y_test_global > 0) & (y_test_global < OTHER_CLASS_ID)).sum():,}}, Zero-Day Other={{(y_test_global==OTHER_CLASS_ID).sum():,}}")

    # -- Step B: Train Stage 1 Binary Defense (Normal vs Attack) -----------------
    v10_bin_dir = MODEL_DIR / "v10_binary_defense"
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
        print(f"  [OK] V10 Binary Defense trained in {{time.perf_counter()-t_vb:.1f}}s")

    # -- Step C: Train Stage 2 Known Attack Classifier --------------------------
    atk_train_mask = (y_train_s == 1)
    atk_dev_mask   = (y_dev_s == 1)
    
    X_tr_atk = X_train_ext_s[atk_train_mask]
    lbl_tr_atk = lbl_train_s[atk_train_mask]
    X_dv_atk = X_dev_ext_s[atk_dev_mask]
    lbl_dv_atk = lbl_dev_s[atk_dev_mask]

    known_atk_to_local_id = {{atk: i for i, atk in enumerate(known_attacks)}}
    local_id_to_global_id = {{i: ATTACK_TO_ID[atk] for atk, i in known_atk_to_local_id.items()}}

    y_tr_atk_local = np.array([known_atk_to_local_id[l] for l in lbl_tr_atk], dtype=np.int64)
    y_dv_atk_local = np.array([known_atk_to_local_id[l] for l in lbl_dv_atk], dtype=np.int64)

    atk_cls_dir = MODEL_DIR / "v10_attack_classifier"
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
        
        attack_model, hist_atk = train_with_resume(
            attack_model, atk_cls_dir,
            X_tr_atk, y_tr_atk_local,
            X_dv_atk, y_dv_atk_local,
            CONFIG["attack_classifier_epochs"], RUN_SEED + 30_000, "V10 Attack Classifier", CONFIG,
            custom_loss_weights=aw_t
        )
        hist_atk.to_csv(atk_cls_dir / "history.csv", index=False)
        seed_SM.mark_done("v10_attack_cls_train", {{"seconds": time.perf_counter() - t_va}})
        print(f"  [OK] V10 Attack Classifier trained in {{time.perf_counter()-t_va:.1f}}s")

    # -- Step D: Initialize Hierarchical Pipeline --------------------------------
    hierarchical_ids = HierarchicalIDS(
        binary_model=v10_bin_model,
        attack_model=attack_model,
        attack_id_to_global_id=local_id_to_global_id,
        other_class_id=OTHER_CLASS_ID,
        tau=CONFIG["rejection_threshold"]
    )

    # -- Step E: Baseline & Paper Defense Benchmarks -----------------------------
    baseline_dir = MODEL_DIR / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    v9_base_ckpt = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "seeds" / str(RUN_SEED) / "models" / "baseline" / "best.pt"
    baseline = IDSNet(len(paper_idx_local), num_classes=2).to(DEVICE)
    if (baseline_dir / "best.pt").exists():
        baseline.load_state_dict(torch.load(baseline_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    elif v9_base_ckpt.exists():
        shutil.copy2(v9_base_ckpt, baseline_dir / "best.pt")
        baseline.load_state_dict(torch.load(v9_base_ckpt, map_location=DEVICE, weights_only=False)["model_state_dict"])
    else:
        baseline, _ = train_with_resume(
            baseline, baseline_dir, X_train_paper, y_train, X_dev_paper, y_dev,
            CONFIG["baseline_epochs"], RUN_SEED, "Baseline", CONFIG
        )

    paper_dir = MODEL_DIR / "paper_defense"
    paper_dir.mkdir(parents=True, exist_ok=True)
    v9_paper_ckpt = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "seeds" / str(RUN_SEED) / "models" / "paper_defense" / "best.pt"
    paper_model = IDSNet(len(paper_idx_local), num_classes=2).to(DEVICE)
    if (paper_dir / "best.pt").exists():
        paper_model.load_state_dict(torch.load(paper_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    elif v9_paper_ckpt.exists():
        shutil.copy2(v9_paper_ckpt, paper_dir / "best.pt")
        paper_model.load_state_dict(torch.load(v9_paper_ckpt, map_location=DEVICE, weights_only=False)["model_state_dict"])
    else:
        paper_model, _ = train_with_resume(
            paper_model, paper_dir, X_train_paper, y_train, X_dev_paper, y_dev,
            CONFIG["baseline_epochs"], RUN_SEED, "Paper Defense", CONFIG
        )

    # -- Step F: Evaluation Sample Selection -------------------------------------
    eval_ids_path = SEED_DIR / "eval_ids.npz"
    v9_eval_ids_p = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "seeds" / str(RUN_SEED) / "eval_ids.npz"
    if eval_ids_path.exists():
        eval_ids = np.load(eval_ids_path)["eval_ids"]
    elif v9_eval_ids_p.exists():
        shutil.copy2(v9_eval_ids_p, eval_ids_path)
        eval_ids = np.load(eval_ids_path)["eval_ids"]
    else:
        rng = np.random.RandomState(RUN_SEED)
        eval_ids = rng.choice(len(X_test_mi), min(CONFIG["eval_n"], len(X_test_mi)), replace=False)
        atomic_save_numpy(eval_ids_path, eval_ids=eval_ids)

    X_ev_paper = X_test_paper[eval_ids]
    X_ev_ext   = X_test_ext[eval_ids]
    y_ev_bin   = y_test[eval_ids]
    y_ev_multi = y_test_global[eval_ids]

    bl_clean_p, _  = predict_model(baseline, X_ev_paper)
    pp_clean_p, _  = predict_model(paper_model, X_ev_paper)
    v10_multi_p, v10_bin_p, _ = hierarchical_ids.predict(X_ev_ext)

    eval_models = [
        (baseline,      "Baseline",      X_ev_paper, paper_bounds, paper_mask, bl_clean_p),
        (paper_model,   "Paper Defense", X_ev_paper, paper_bounds, paper_mask, pp_clean_p),
        (v10_bin_model, "V10 Defense",   X_ev_ext,   ext_bounds,   ext_mask,   v10_bin_p),
    ]

    rows = []
    bl_metrics  = compute_metrics(y_ev_bin, bl_clean_p)
    pp_metrics  = compute_metrics(y_ev_bin, pp_clean_p)
    v10_metrics = compute_metrics(y_ev_bin, v10_bin_p)
    v10_mc_met  = compute_multiclass_eval(y_ev_multi, v10_multi_p, ID_TO_LABEL)

    rows.append({{"method": "Baseline",      "attack": "Clean", "seed": RUN_SEED, **bl_metrics}})
    rows.append({{"method": "Paper Defense", "attack": "Clean", "seed": RUN_SEED, **pp_metrics}})
    rows.append({{"method": "V10 Defense",   "attack": "Clean", "seed": RUN_SEED, **v10_metrics, **v10_mc_met}})

    print(f"  [CLEAN] Baseline acc={{bl_metrics['accuracy']:.4f}} | Paper Defense acc={{pp_metrics['accuracy']:.4f}}")
    print(f"  [CLEAN] V10 Binary acc={{v10_metrics['accuracy']:.4f}} | Multiclass macro-F1={{v10_mc_met['multi_macro_f1']:.4f}}")

    # -- Step G: FGSM Attack Evaluation ------------------------------------------
    print("  Evaluating FGSM (eps=0.05)...")
    for model_obj, name, X_ev, bnds, msk, clean_p in eval_models:
        t_a = time.perf_counter()
        adv = fgsm_attack(model_obj, X_ev, y_ev_bin, CONFIG["attack_epsilon"], bnds, msk)
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_ev_bin, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_ev_bin, clean_p, adv_p)
        
        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi, adv_multi, ID_TO_LABEL)
            
        rows.append({{"method": name, "attack": "FGSM", "seed": RUN_SEED, **metrics, **pert, **extra}})
        print(f"    FGSM {{name}}: acc={{metrics['accuracy']:.4f}}  ASR={{pert['attack_success_rate']:.4f}} ({{time.perf_counter()-t_a:.1f}}s)")

    # -- Step H: PGD-100 Attack Evaluation ---------------------------------------
    print("  Evaluating PGD-100 (eps=0.05)...")
    for model_obj, name, X_ev, bnds, msk, clean_p in eval_models:
        t_a = time.perf_counter()
        adv = pgd_attack(model_obj, X_ev, y_ev_bin,
                         CONFIG["attack_epsilon"], CONFIG["pgd_steps_eval"],
                         CONFIG["pgd_restarts"], bnds, msk, seed=RUN_SEED)
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_ev_bin, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_ev_bin, clean_p, adv_p)

        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi, adv_multi, ID_TO_LABEL)

        rows.append({{"method": name, "attack": "PGD", "seed": RUN_SEED, **metrics, **pert, **extra}})
        print(f"    PGD {{name}}: acc={{metrics['accuracy']:.4f}}  ASR={{pert['attack_success_rate']:.4f}} ({{time.perf_counter()-t_a:.1f}}s)")

    # -- Step I: Square-style Attack (Black-box) ---------------------------------
    print("  Evaluating Square-style Attack (black-box)...")
    sq_n  = min(CONFIG["square_eval_n"], len(X_ev_paper))
    y_sq  = y_ev_bin[:sq_n]
    for model_obj, name, X_ev, bnds, clean_p in [
        (baseline,      "Baseline",      X_ev_paper[:sq_n], paper_bounds, bl_clean_p[:sq_n]),
        (paper_model,   "Paper Defense", X_ev_paper[:sq_n], paper_bounds, pp_clean_p[:sq_n]),
        (v10_bin_model, "V10 Defense",   X_ev_ext[:sq_n],   ext_bounds,   v10_bin_p[:sq_n]),
    ]:
        adv  = square_style_attack(model_obj, X_ev, CONFIG["attack_epsilon"], bounds=bnds, n_iters=CONFIG["square_iterations"], seed=RUN_SEED)
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_sq, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_sq, clean_p, adv_p)
        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi[:sq_n], adv_multi, ID_TO_LABEL)
        rows.append({{"method": name, "attack": "Square-style Attack", "seed": RUN_SEED, **metrics, **pert, **extra}})

    # -- Step J: Full Held-Out Zero-Day Test Evaluation --------------------------
    zd_test_mask = (y_test_global == OTHER_CLASS_ID)
    if zd_test_mask.sum() > 0:
        X_zd_test = X_test_ext[zd_test_mask]
        zd_preds, zd_bin_preds, _ = hierarchical_ids.predict(X_zd_test)
        zd_caught_as_attack = float((zd_bin_preds == 1).mean())
        zd_isolated_as_other = float((zd_preds == OTHER_CLASS_ID).mean())
        print(f"\\\\n  [FULL ZERO-DAY EVALUATION ({{zd_test_mask.sum():,}} flows of held-out '{{held_out_attack}}')]")
        print(f"    Detected as Attack by Stage 1: {{zd_caught_as_attack*100:.2f}}%")
        print(f"    Correctly Isolated as 'Other': {{zd_isolated_as_other*100:.2f}}%")

    # -- Step K: Save Seed Results -----------------------------------------------
    df_seed_{seed_num} = pd.DataFrame(rows)
    atomic_save_df(df_seed_{seed_num}, SEED_DIR / "seed_results.csv")
    atomic_save_json({{"seed": RUN_SEED, "seconds": time.perf_counter()-t_seed_start, "status": "complete"}}, SEED_DIR / "seed_complete.json")
    cm = confusion_matrix(y_ev_multi, v10_multi_p)
    atomic_save_numpy(SEED_DIR / "confusion_matrix.npz", cm=cm)
    seed_SM.mark_done("seed_complete")
    print(f"\\\\n[OK] Seed {{RUN_SEED}} execution complete in {{time.perf_counter()-t_seed_start:.1f}}s.")"""

    # -------------------------------------------------------------
    # Cell 18
    # -------------------------------------------------------------
    add_cell("code", generate_seed_cell(42, 18))

    # -------------------------------------------------------------
    # Cell 19
    # -------------------------------------------------------------
    add_cell("code", generate_seed_cell(123, 19))

    # -------------------------------------------------------------
    # Cell 20
    # -------------------------------------------------------------
    add_cell("code", generate_seed_cell(2024, 20))

'''

new_builder_code = prefix + seed_generator_code + suffix
with open(builder_file, "w", encoding="utf-8") as f:
    f.write(new_builder_code)

print(f"[SUCCESS] Updated {builder_file} with unified, bug-free seed cell generation.")
