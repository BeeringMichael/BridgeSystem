"""
Data Processing Pipeline for Bridge Bidding BERT Model
Handles data loading, tokenization, and preparation for training.
"""

import json
import os
from typing import List, Dict, Tuple

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer

class BridgeBiddingDataset(Dataset):
    """Dataset class for bridge bidding data."""
    
    def __init__(self, data_path: str, tokenizer: BertTokenizer, max_length: int = 128):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = self._load_data(data_path)
    
    def _load_data(self, data_path: str) -> List[Dict]:
        """Load and preprocess data from JSON file."""
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Filter and validate data
        processed_data = []
        for item in data:
            if 'input' in item and 'target' in item:
                processed_data.append({
                    'input_text': item['input'],
                    'target': item['target']
                })
        
        return processed_data
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        # Tokenize input text
        encoding = self.tokenizer(
            item['input_text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Create target encoding (contract as text)
        target_encoding = self.tokenizer(
            item['target'],
            max_length=10,  # Contract is short (e.g., "1S", "3NT")
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': target_encoding['input_ids'].flatten(),
            'label_mask': target_encoding['attention_mask'].flatten()
        }

def create_data_loaders(
    data_path: str,
    model_name: str = 'bert-base-uncased',
    batch_size: int = 16,
    max_length: int = 128
) -> Tuple[DataLoader, DataLoader, BertTokenizer]:
    """Create training and validation data loaders."""
    
    # Initialize tokenizer
    tokenizer = BertTokenizer.from_pretrained(model_name)
    
    # Load dataset
    dataset = BridgeBiddingDataset(data_path, tokenizer, max_length)
    
    # Split into train and validation (80-20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False
    )
    
    return train_loader, val_loader, tokenizer

def generate_synthetic_data(num_samples: int = 10000):
    """Generate synthetic bridge bidding data if needed."""
    from src.data_generator import generate_dataset
    
    os.makedirs('data', exist_ok=True)
    generate_dataset(num_samples, 'data/bridge_bidding_synthetic.json')
    print(f"Generated {num_samples} synthetic bridge bidding examples")

if __name__ == '__main__':
    # Generate data if it doesn't exist
    if not os.path.exists('data/bridge_bidding_synthetic.json'):
        generate_synthetic_data()
    
    # Test data loading
    train_loader, val_loader, tokenizer = create_data_loaders(
        'data/bridge_bidding_synthetic.json',
        batch_size=8
    )
    
    print(f"Tokenizer vocab size: {tokenizer.vocab_size}")
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}")
    
    # Test a batch
    batch = next(iter(train_loader))
    print(f"Input shape: {batch['input_ids'].shape}")
    print(f"Attention mask shape: {batch['attention_mask'].shape}")
    print(f"Labels shape: {batch['labels'].shape}")
    print(f"Sample input: {tokenizer.decode(batch['input_ids'][0])}")
    print(f"Sample target: {tokenizer.decode(batch['labels'][0])}")