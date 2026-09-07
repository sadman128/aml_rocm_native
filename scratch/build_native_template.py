import os
from pptx import Presentation

def robust_replace(shape, replacement_dict):
    if hasattr(shape, 'text_frame') and shape.text_frame is not None:
        full_text = shape.text_frame.text.replace('\n', ' ').strip()
        if not full_text: return
        
        for key, new_val in replacement_dict.items():
            clean_key = key.replace('\n', ' ').strip()
            if clean_key and (clean_key == full_text or clean_key in full_text):
                # Preserve formatting of the first valid run
                first_run = None
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        if r.text.strip():
                            first_run = r
                            break
                    if first_run: break
                
                font_name, font_size, font_bold, font_italic, font_color = None, None, None, None, None
                if first_run and first_run.font:
                    font_name = first_run.font.name
                    font_size = first_run.font.size
                    font_bold = first_run.font.bold
                    font_italic = first_run.font.italic
                    if first_run.font.color and getattr(first_run.font.color, 'type', None):
                        try:
                            font_color = first_run.font.color.rgb
                        except:
                            font_color = None
                
                # Clear all paragraphs
                for p in shape.text_frame.paragraphs:
                    p.clear()
                    
                p = shape.text_frame.paragraphs[0]
                new_r = p.add_run()
                new_r.text = new_val
                
                if font_name: new_r.font.name = font_name
                if font_size: new_r.font.size = font_size
                if font_bold is not None: new_r.font.bold = font_bold
                if font_italic is not None: new_r.font.italic = font_italic
                if font_color: new_r.font.color.rgb = font_color
                break  # stop checking dict for this shape

    if hasattr(shape, 'has_table') and shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                robust_replace(cell, replacement_dict)
                
    if getattr(shape, 'shape_type', None) == 6:  # Group
        for shp in shape.shapes:
            robust_replace(shp, replacement_dict)


TEMPLATE_PATH = r"F:\PythonProjects\aml_rocm_native\docs\pre_defense\slide templates\Modern Product Feature Comparison Infographic Presentation.pptx"
OUTPUT_PATH = r"F:\PythonProjects\aml_rocm_native\docs\pre_defense\PreDefense_Presentation_Native.pptx"

print("Loading original template...")
prs = Presentation(TEMPLATE_PATH)

# Dictionaries for the 6 infographic slides we are keeping
dict_s0 = {
    "Feature Evaluation Stages": "Literature Review: Macro Findings",
    "Four levels to measure product features": "Survey of 40 Peer-Reviewed Publications (2021–2026)",
    "Check if the feature covers essential needs": "Clean accuracy drop (2%–6%) due to adversarial training",
    "Identify premium features delivering maximum": "Tree ensembles highly vulnerable to iterative perturbations",
    "Evaluate consistency, reliability, and stability": "Static adversarial samples lose effectiveness (staleness)",
    "Measure additional functions that extend": "XAI gates incur 85–220 ms/flow latency",
    "Assess day-to-day usefulness": "Clean SHAP retains vulnerable socket shortcuts",
    "Basic Fit": "1. Trade-Off",
    "Peak Value": "2. Trees",
    "Standard Quality": "3. Staleness",
    "Advanced Use": "4. Latency",
    "Practical Value": "5. Shortcuts"
}

dict_s1 = {
    "Feature Review Steps": "Methodology 1: Data Sanitization",
    "Four key stages to review product features": "Zero-Leakage Partitioning & Mutual Information",
    "Select the core requirements that guide": "Remove Src/Dst IP, Src/Dst Port, Timestamp, Flow ID",
    "Gather reliable information on product": "Lock 80% Dev (72% Train/8% Val) and 20% Test",
    "Compare feature sets to measure": "Filter 69 features to top 40 candidates using Shannon MI",
    "Summarize strengths and weaknesses": "Balance continuous features within training split only",
    "Identify Needs": "1. Socket Removal",
    "Collect Data": "2. Zero-Leakage Split",
    "Analyze Features": "3. MI Screening",
    "Draw Insights": "4. SMOTE Balancing"
}

dict_s3 = {
    "Feature Selection Stages": "Methodology 2: Stability SHAP",
    "Step-by-step process to identify": "Isolating the 27 Perturbation-Invariant Features",
    "Start by listing every available": "Train unhardened baseline canary model on clean data.",
    "Exclude features that fail": "Subject canary to 20-step PGD (ε=0.05). Compute absolute SHAP.",
    "Retain only the features that": "Calculate Stability Score Sⱼ combining clean and adversarial attributions.",
    "Prioritize features that show": "Select minimal subset reaching 80% cumulative stability mass.",
    "Select the most effective combination": "Result: 27 robust features retained, 13 gradient-volatile pruned.",
    "All Options": "1. Canary Model",
    "Filter Basics": "2. Dual-State Audit",
    "Quality Check": "3. Score Sⱼ",
    "Value Rank": "4. 80% Mass Rule",
    "Final Pick": "5. Final 27 Features"
}

dict_s4 = {
    "Key Comparison Points": "Expected Results & Targets",
    "Six criteria used to compare": "Performance targets & multi-threat evaluation protocol",
    "Verify the speed, efficiency": "Target ≥ 95.5% clean accuracy, reducing the AT penalty.",
    "Confirm compliance with safety": "Target 88.0%–90.5% robust accuracy against 100-step PGD.",
    "Assess long-term strength": "Maintain sub-0.05 ms inference for line-rate deployment.",
    "Review environmental impact": "Achieve < 12.0% ASR across white-box iterative attacks.",
    "Ensure smooth integration": "Protocol: FGSM, PGD, BIM, APGD, C&W, Square.",
    "Check ease of maintenance": "Verify genuine robustness (no gradient obfuscation).",
    "Performance Test": "Clean Accuracy",
    "Safety Standard": "Robust Accuracy",
    "Durability Score": "Inference Speed",
    "Sustainability Level": "ASR Limit",
    "Compatibility Check": "Threat Protocol",
    "Support Access": "Verification"
}

dict_s5 = {
    "Feature Impact Levels": "Problem Statement",
    "Four ways features affect user choice": "Vulnerability of DNN-NIDS to bounded perturbations",
    "Enhances overall satisfaction by improving": "Modern DNNs hit >95% clean accuracy but drop to 30-40% under PGD attacks.",
    "Shows the features ability to reduce": "Classifiers rely on gradient-volatile features that attackers easily manipulate.",
    "Acts as the decisive factor that strongly": "Models memorize transient IP/Port shortcuts instead of general traffic behavior.",
    "Highlights how the feature increases": "Static adversarial samples generated before training lose alignment with the boundary.",
    "Experience Boost": "Accuracy vs. Robustness",
    "Cost Saving": "Volatile Features",
    "Decision Driver": "Shortcut Memorization",
    "Convenience Gain": "Static Defense Staleness"
}

dict_s7 = {
    "Comparison Decision Flow": "Methodology 3: Two-Phase Training",
    "Three main routes guide": "Curriculum Optimization: Clean Warmup + Online PGD",
    "Identify the main goals": "Epochs 1–10: Train exclusively on clean data.",
    "Pick the option that best matches": "Epochs 11–50: Generate fresh 5-step online PGD perturbations per batch.",
    "Finalize the decision by choosing": "Balances L_clean and L_adv (0.5/0.5) using current weights.",
    "Start Needs": "Phase 1: Warmup",
    "Choose Path": "Phase 2: Dynamic PGD",
    "Confirm Pick": "Joint Objective",
    "Define core problems": "Weights settle in stable basin",
    "Clarify priority functions": "Attack/benign clusters form",
    "Compare different options": "Tracks shifting boundary",
    "Match the feature set": "Mitigates attack staleness",
    "Validate that the final choice": "Preserves Phase 1 geometry",
    "Ensure the decision aligns": "Completed in ~70 mins"
}

dict_s9 = {
    "Key Strengths": "Holla (Base)",
    "Main Limits": "Olukola (AMDS)",
    "Cost Level": "Güvenç Paltun",
    "User Support": "Zeng (CSAGC)",
    "Option A": "Holla et al.",
    "Option B": "Olukola & Rahimi",
    "Option C": "Güvenç Paltun",
    "Option D": "Zeng et al.",
    "Reliable speed with stable function": "Static triad augmentation. baseline 85% drops to 55%. Retains port shortcuts.",
    "High performance though less stable": "Two-stage dynamic AT on all 78 dimensions (+140% overhead). 0.08ms latency.",
    "Moderate performance suited for standard": "Runtime XAI gate. 85-220 ms latency (too slow). Vulnerable to scaffolding.",
    "Advanced performance with premium": "Dynamic graph attention. >2.4 ms latency. Topology spoofing risks.",
    "Simple layout that is clear and practical": "Limitation: Static attack staleness",
    "Flexible design offering multiple": "Limitation: Full-dimensional burden",
    "Minimal design focused on ease": "Limitation: Prohibitive runtime delay",
    "Detailed design built for professional": "Limitation: Topology evasion risks"
}

print("Replacing text in existing infographic slides...")
slides_list = list(prs.slides)
for shape in slides_list[0].shapes: robust_replace(shape, dict_s0)
for shape in slides_list[1].shapes: robust_replace(shape, dict_s1)
for shape in slides_list[3].shapes: robust_replace(shape, dict_s3)
for shape in slides_list[4].shapes: robust_replace(shape, dict_s4)
for shape in slides_list[5].shapes: robust_replace(shape, dict_s5)
for shape in slides_list[7].shapes: robust_replace(shape, dict_s7)
for shape in slides_list[9].shapes: robust_replace(shape, dict_s9)

print("Adding standard text slides...")
def add_bullets(title, bullets, layout_idx=1):
    sl = prs.slides.add_slide(prs.slide_layouts[layout_idx])
    sl.shapes.title.text = title
    tf = sl.placeholders[1].text_frame
    tf.text = bullets[0]
    for b in bullets[1:]:
        p = tf.add_paragraph()
        p.text = b
        p.level = 0
    return sl

# Create the 7 new standard slides (they append to the end, indices 10 to 16)
# 10: Title
sl_title = prs.slides.add_slide(prs.slide_layouts[0])
sl_title.shapes.title.text = "Adversarial Robustness in Network Intrusion Detection Systems"
sl_title.placeholders[1].text = "via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training\nSadman Hossain Sajid & Redoan Islam"

# 11: Outline
add_bullets("Presentation Outline", [
    "1. Research Context & Problem Statement",
    "2. Motivation & Research Objectives",
    "3. Literature Review (Macro Findings & Benchmark Defenses)",
    "4. Comparative Analysis & Research Gaps",
    "5. Proposed Methodology (Data Sanitization, Stability SHAP, Two-Phase PGD)",
    "6. Dataset & Computing Environment",
    "7. Target Model Architecture",
    "8. Weekly Research Timeline & Gantt Chart",
    "9. Expected Results & Research Hypotheses",
    "10. Conclusion & Immediate Next Steps"
])

# 12: Motivation
add_bullets("Motivation & Research Objectives", [
    "Real-Time Cloud Requirements: High-speed networks require sub-0.05 ms per-flow inference.",
    "The Accuracy vs. Robustness Trade-off: Investigate if isolating stable features mitigates the clean accuracy penalty.",
    "Benchmark Hygiene: Permanently excise socket identifiers (IPs, Ports) to eliminate shortcut learning.",
    "Zero-Leakage: Enforce strict data partitioning before normalization."
])

# 13: Comparative Analysis
add_bullets("Comparative Analysis & Research Gaps", [
    "Holla et al. (Base Paper): Retains port shortcuts, suffers from static attack staleness.",
    "Olukola & Rahimi: Two-stage dynamic AT but operates on all 78 dimensions (+140% overhead).",
    "Güvenç Paltun et al.: Runtime XAI verification is too slow (85–220 ms/flow).",
    "Zeng et al.: Dynamic graph buffering introduces >2.4 ms delay.",
    "Our Pipeline: Bridges all gaps — reduces staleness via dynamic PGD, isolates stable features via SHAP, maintains line-rate inference."
])

# 14: Dataset & Env
add_bullets("Dataset, Environment & Architecture", [
    "Dataset: CSE-CIC-IDS2018 (6,320,003 valid flows)",
    "Strict Split: 72% Core Train / 8% Validation / 20% Frozen Test",
    "Hardware: AMD Radeon RX 7600 (8 GB VRAM), RDNA 3",
    "Software: Python 3.10, native ROCm on Windows, ART library",
    "Architecture: 4-Layer MLP (27 → 128 → 64 → 32 → 2)",
    "Layer Design: Linear → BatchNorm → ReLU → Dropout(0.30)"
])

# 15: Gantt
add_bullets("Weekly Research Timeline", [
    "Weeks 1–7 (COMPLETED): Topic Selection, Literature Review, Methodology Study, Environment Setup.",
    "Sep 10 Milestone: Pre-Defense Presentation (Current Status).",
    "Weeks 11–12 (UPCOMING): Implementation & Empirical Evaluation.",
    "Weeks 13–14 (UPCOMING): Result Analysis & Final Manuscript Drafting.",
    "Oct 11 Milestone: Final Thesis Defense."
])

# 16: Conclusion
add_bullets("Conclusion & Immediate Next Steps", [
    "Theoretical: 80% cumulative stability-mass rule isolates a 27-dimensional perturbation-invariant subspace.",
    "Architectural: Clean warmup + 5-step online PGD (α=0.005) reduces staleness.",
    "Methodological: Socket shortcuts purged; zero-leakage 72/8/20 partitioning enforced.",
    "Next Steps: Execute 3-seed runs across 9 threat models. Submit final manuscript for Oct 11 defense."
])

print("Reordering slides to match 14-slide sequence...")
# Current indices:
# 0-9: original templates (0=LitRev1, 1=Meth1, 2=drop, 3=Meth2, 4=Results, 5=Prob, 6=drop, 7=Meth3, 8=drop, 9=LitRev2)
# 10: Title
# 11: Outline
# 12: Motivation
# 13: Comp Table
# 14: Dataset
# 15: Gantt
# 16: Conclusion

# Target Order (0 to 13):
# 1. Title (10)
# 2. Outline (11)
# 3. Problem (5)
# 4. Motivation (12)
# 5. Lit Rev 1 (0)
# 6. Lit Rev 2 (9)
# 7. Comp Table (13)
# 8. Meth 1 (1)
# 9. Meth 2 (3)
# 10. Meth 3 (7)
# 11. Dataset (14)
# 12. Gantt (15)
# 13. Results (4)
# 14. Conclusion (16)

target_order = [10, 11, 5, 12, 0, 9, 13, 1, 3, 7, 14, 15, 4, 16]
all_slides = list(prs.slides._sldIdLst)

# Clear existing order in xml
prs.slides._sldIdLst.clear()

# Re-append in desired order
for idx in target_order:
    prs.slides._sldIdLst.append(all_slides[idx])

# The unused slides (2, 6, 8) are naturally dropped because we don't append them back!

print("Saving...")
prs.save(OUTPUT_PATH)
print(f"✅ DONE! Saved to {OUTPUT_PATH}")
