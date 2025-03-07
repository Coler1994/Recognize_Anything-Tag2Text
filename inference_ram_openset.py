'''
 * The Recognize Anything Model (RAM) inference on unseen classes
 * Written by Xinyu Huang
'''
import argparse
import numpy as np
import random

import torch
import torchvision.transforms as transforms

from PIL import Image
from ram.models import ram
from ram import inference_ram_openset as inference

from ram.utils import build_openset_label_embedding
from torch import nn

parser = argparse.ArgumentParser(
    description='Tag2Text inferece for tagging and captioning')
parser.add_argument('--image',
                    metavar='DIR',
                    help='path to dataset',
                    default='images/openset_example.jpg')
parser.add_argument('--pretrained',
                    metavar='DIR',
                    help='path to pretrained model',
                    default='pretrained/tag2text_swin_14m.pth')
parser.add_argument('--image-size',
                    default=384,
                    type=int,
                    metavar='N',
                    help='input image size (default: 448)')


if __name__ == "__main__":

    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    transform = transforms.Compose([
        transforms.Resize((args.image_size, args.image_size)),
        transforms.ToTensor(), normalize
    ])

    #######load model
    model = ram(pretrained=args.pretrained,
                             image_size=args.image_size,
                             vit='swin_l')
    
    #######set openset interference
    openset_label_embedding, openset_categories = build_openset_label_embedding()

    model.tag_list = np.array(openset_categories)
    
    model.label_embed = nn.Parameter(openset_label_embedding.float())

    model.num_class = len(openset_categories)
    # the threshold for unseen categories is often lower
    model.class_threshold = torch.ones(model.num_class) * 0.5
    #######

    model.eval()

    model = model.to(device)
    raw_image = Image.open(args.image).convert("RGB").resize(
        (args.image_size, args.image_size))
    image = transform(raw_image).unsqueeze(0).to(device)

    res = inference(image, model)
    print("Image Tags: ", res)
