import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import streamlit as st
from monai.networks.nets import DynUNet

# --- Exact Class Definitions from your Snippets ---

class BrainTumorClassifier(nn.Module):
    def __init__(self, num_classes=4):
        super(BrainTumorClassifier, self).__init__()
        self.feature_layers = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=4, stride=1, padding=1),
            nn.ReLU(inplace=False),
            nn.MaxPool2d(kernel_size=3),
            nn.Conv2d(32, 64, kernel_size=4, stride=1, padding=1),
            nn.ReLU(inplace=False),
            nn.MaxPool2d(kernel_size=3),
            nn.Conv2d(64, 128, kernel_size=4, stride=1, padding=1),
            nn.ReLU(inplace=False),
            nn.MaxPool2d(kernel_size=3)
        )
        self.flatten = nn.Flatten()
        self.dense_layers = nn.Sequential(
            nn.Linear(128 * 5 * 5, 512),
            nn.ReLU(inplace=False),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        x = self.feature_layers(x)
        x = self.flatten(x)
        x = self.dense_layers(x)
        return x

class TumorSizeCalculator(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.transform = transforms.Compose([transforms.ToTensor()])

    def forward(self, x):
        # x is assumed to be a PIL Image already from the UI
        x = x.convert('L')
        x = self.transform(x)
        return torch.mean(x).item()

@st.cache_resource
def load_all_models():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Load Classification
    clf = BrainTumorClassifier(num_classes=4)
    clf = torch.load("models/classification.pth", map_location=device)
    clf.eval()

    # 2. Load Segmentation (DynUNet)
    seg = DynUNet(
        spatial_dims=2,
        in_channels=1,
        out_channels=1,
        kernel_size=[3, 3, 3, 3, 3],
        strides=[1, 2, 2, 2, 2],
        upsample_kernel_size=[2, 2, 2, 2],
        filters=[16, 32, 64, 128, 256],
    )
    seg.load_state_dict(torch.load("models/segmentation.pth", map_location=device))
    seg.eval()

    # 3. Load Size Model
    size_m = torch.load("models/size_estimation.pth", map_location=device)
    size_m.eval()

    return clf, seg, size_m, device

class MedicalEngine:
    def __init__(self):
        self.clf, self.seg, self.size_m, self.device = load_all_models()
        
        self.clf_transform = transforms.Compose([
            transforms.Resize((150, 150)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def run_classification(self, pil_img):
        img_t = self.clf_transform(pil_img.convert('RGB')).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.clf(img_t)
            probs = F.softmax(output, dim=1)
            conf, pred = torch.max(probs, 1)
        return pred.item(), conf.item(), probs.cpu().numpy()[0]

    def run_segmentation(self, pil_img):
        # Resize to 256x256 as per your TestDataset logic
        img_gray = pil_img.convert('L').resize((256, 256), resample=Image.NEAREST)
        img_np = np.array(img_gray).astype(np.float32) / 255.0
        img_t = torch.tensor(img_np).unsqueeze(0).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            pred = self.seg(img_t)
            mask = torch.sigmoid(pred).squeeze().cpu().numpy()
        return (mask > 0.5).astype(np.uint8)

    def run_size_estimation(self, pil_img):
        with torch.no_grad():
            size_val = self.size_m(pil_img)
        return size_val