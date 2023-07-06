provider "aws" {
        access_key = ""
        secret_key = ""
        region = var.region_name
}

resource "aws_instance" "test" {
  ami                           = var.image_id
  instance_type                 = var.instance_type
  vpc_security_group_ids        = ["${aws_security_group.webserversg.id}"]

  key_name                      = aws_key_pair.terraform-key-pair.id

  tags = {
    Name = var.tag_name
  }
}

resource "aws_key_pair" "terraform-key-pair" {
  key_name      = "ssh key pair 이름 아마 private 키 이름이랑 같을 듯"
  public_key    = file("ssh public key 경로")

  tags          = {
        description = "terraform key pair import"
  }
}

resource "aws_security_group" "webserversg" {
  name        = "webserversg"
}


resource "aws_security_group_rule" "websg_http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.webserversg.id
  description       = "http"
}

resource "aws_security_group_rule" "websg_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.webserversg.id
  description       = "ssh"
}

resource "aws_security_group_rule" "websg_outbound" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.webserversg.id
  description       = "outbound"
}