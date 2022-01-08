#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()
    
    logger.info(f"Downloading artifact {args.input_artifact}")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    
    logger.info(f"Cleaning with min price {args.min_price} and max price {args.max_price}")
    
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    
    logger.info(f"Saving cleaned data to {args.output_artifact}")
    
    df.to_csv(args.output_artifact, index=False)
    
    logger.info(f"Uploading artifact {args.output_artifact}")
    
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name of input CSV file",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum value for the price filter for cleaned data",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum value for the price filter for cleaned data",
        required=True
    )


    args = parser.parse_args()

    go(args)
