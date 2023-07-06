variable "image_id" {
  type    = string
  default = "ami-0261755bbcb8c4a84"
}

variable "region_name" {
  type    = string
  default = "ap-northeast-2"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "tag_name" {
  type     = string
  nullable = true
}