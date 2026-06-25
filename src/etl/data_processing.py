import argparse
import pandas as pd
from pathlib import Path

def main(input_dir: str, output_file: str):
    """
    Process all CSV files in input directory and aggregate them into one train.parquet file
    """
    try:
        # Validate input directory
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
        
        if not input_path.is_dir():
            raise NotADirectoryError(f"Input path is not a directory: {input_dir}")
        
        # Find all CSV files in input directory
        csv_files = list(input_path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in directory: {input_dir}")
        
        print(f"Found {len(csv_files)} CSV files in {input_dir}")
        
        # Create list to hold all dataframes
        dataframes = []
        
        # Process each CSV file
        for csv_file in csv_files:
            try:
                print(f"Processing: {csv_file.name}")
                
                # Read CSV file using pandas
                df = pd.read_csv(csv_file)
                print(f"  DataFrame shape: {df.shape}")
                print(f"  Columns: {list(df.columns)}")
                
                # Convert string columns to numeric where possible
                for column in df.columns:
                    if df[column].dtype == 'object':
                        # Try to convert to numeric
                        numeric_series = pd.to_numeric(df[column], errors='coerce')
                        # Check if conversion was successful (more than 50% converted)
                        if numeric_series.notna().sum() > len(df) * 0.5:
                            df[column] = numeric_series
                            print(f"  Converted column '{column}' to numeric")
                
                df.dropna()
                
                # Add dataframe to list
                dataframes.append(df)
                print(f"  Added to aggregation")
                
            except Exception as e:
                print(f"  Error processing {csv_file.name}: {str(e)}")
                continue
        
        if not dataframes:
            raise ValueError("No CSV files were successfully processed")
        
        # Concatenate all dataframes
        print(f"\nAggregating {len(dataframes)} dataframes...")
        combined_df = pd.concat(dataframes, ignore_index=True)
        print(f"Combined DataFrame shape: {combined_df.shape}")
        
        # Drop rows with null values in target column
        # Assuming 'target' column exists - adjust column name as needed
        target_column = "target"  # Change this to your actual target column name
        if target_column in combined_df.columns:
            original_count = len(combined_df)
            combined_df = combined_df.dropna(subset=[target_column])
            print(f"Dropped {original_count - len(combined_df)} rows due to null values in target column")
        else:
            print(f"Warning: Target column '{target_column}' not found in combined DataFrame")
            print(f"Available columns: {list(combined_df.columns)}")
        
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as parquet
        combined_df.to_parquet(output_file, index=False)
        print(f"Successfully saved combined data to: {output_file}")
        
        # Show final statistics
        print(f"Final DataFrame shape: {combined_df.shape}")
        print(f"Final DataFrame dtypes:\n{combined_df.dtypes}")
        
        print("\nProcessing completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()
    
    main(args.input_dir, args.output_file)
