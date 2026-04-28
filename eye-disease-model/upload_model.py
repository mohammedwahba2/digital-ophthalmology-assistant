from huggingface_hub import upload_folder

upload_folder(
    folder_path="eye_disease_final_cropped.keras",
    repo_id="mohamed-wahba77/eye-disease-model"
)