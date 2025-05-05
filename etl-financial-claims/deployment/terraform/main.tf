provider "aws" {
}

terraform {
  backend "s3" {
  }
}

module "etl_financial_claims_bucket_name" {
  source = "s3::https://s3.amazonaws.com/hippo-tf/modules.zip//wrappers/utils/resource-name/v3"
  name   = "etl-financial-claims"
}

module "etl_financial_claims_tags" {
  source                 = "s3::https://s3.amazonaws.com/hippo-tf/modules.zip//wrappers/utils/resource-tags/v4"
  module_name            = "etl"
  contains_PHI_data      = "false"
  contains_PII_data      = "false"
  contains_PCI_data      = "false"
  data_classification    = "confidential"
  data_owner             = "Diego_Manzur"
}

module "logs_bucket_name" {
  source = "s3::https://s3.amazonaws.com/hippo-tf/modules.zip//wrappers/utils/resource-name/v2"
  name   = "hippo-access-logs"
}

module "s3_etl_financial_claims_bucket" {
  source      = "s3::https://s3.amazonaws.com/hippo-tf/modules.zip//wrappers/storage/s3-bucket/v7"
  bucket_name = module.etl_financial_claims_bucket_name.qualified_name
  logs_bucket = module.logs_bucket_name.qualified_name
  tags        = module.etl_financial_claims_tags.default
}

moved {
  from = module.s3_etl_financial_claims_bucket.aws_s3_bucket.bucket
  to   = module.s3_etl_financial_claims_bucket.module.s3_bucket.aws_s3_bucket.this[0]
}
