from torchvision import transforms
from PIL import Image
from torch.utils.data import Dataset

class CustomLoader(Dataset):
    def __init__(self, csv_file):
        self.data = csv_file
        self.transform = transforms.Compose([
            transforms.ToTensor(), 
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # Carica l'immagine e la trasforma in tensor
        img_path = self.data.iloc[idx]['image_path']  
        image = Image.open(img_path)
        if self.transform:
            image = self.transform(image)
        
        # Ottieni l'etichetta come stringa
        
        label = self.data.iloc[idx]['label']  
        
        split = self.data.iloc[idx]['split']
        
        return image, label, split
