terraform {
  required_providers {
    ionos = {
      source  = "ionos-cloud/ionoscloud"
      version = "~> 6.0"
    }
  }
}

provider "ionos" {
  token = var.ionos_token
}

variable "ionos_token" {
  description = "IONOS Cloud API token"
  type        = string
  sensitive   = true
}

resource "ionos_datacenter" "main" {
  name        = "example-datacenter"
  location    = "de/fra"
  description = "Example datacenter for cost estimation"
}

resource "ionos_server" "web_server" {
  name              = "web-server-01"
  datacenter_id     = ionos_datacenter.main.id
  cores             = 2
  ram               = 4096
  availability_zone = "AUTO"
  cpu_family        = "AMD_OPTERON"

  volume {
    name           = "system"
    size           = 50
    disk_type      = "SSD"
    licence_type   = "LINUX"
    image_name     = "ubuntu:latest"
    image_password = "K3tTj8G14a3EgKyNeeiY"
  }

  nic {
    lan             = ionos_lan.public.id
    dhcp            = true
    firewall_active = true
  }
}

resource "ionos_server" "app_server" {
  name              = "app-server-01"
  datacenter_id     = ionos_datacenter.main.id
  cores             = 4
  ram               = 8192
  availability_zone = "AUTO"
  cpu_family        = "AMD_OPTERON"

  volume {
    name           = "system"
    size           = 100
    disk_type      = "SSD"
    licence_type   = "LINUX"
    image_name     = "ubuntu:latest"
    image_password = "K3tTj8G14a3EgKyNeeiY"
  }

  nic {
    lan             = ionos_lan.private.id
    dhcp            = true
    firewall_active = true
  }
}

resource "ionos_volume" "data_volume" {
  datacenter_id = ionos_datacenter.main.id
  server_id     = ionos_server.app_server.id
  name          = "data-volume"
  size          = 200
  disk_type     = "SSD"
  licence_type  = "OTHER"
}

resource "ionos_lan" "public" {
  datacenter_id = ionos_datacenter.main.id
  public        = true
  name          = "public-lan"
}

resource "ionos_lan" "private" {
  datacenter_id = ionos_datacenter.main.id
  public        = false
  name          = "private-lan"
}

resource "ionos_loadbalancer" "main_lb" {
  datacenter_id = ionos_datacenter.main.id
  name          = "main-loadbalancer"
  nic_ids       = [ionos_server.web_server.primary_nic]
}

resource "ionos_ipblock" "public_ips" {
  location = "de/fra"
  size     = 2
  name     = "public-ip-block"
}

resource "ionos_pg_cluster" "postgres_db" {
  postgres_version       = "15"
  instances              = 1
  cores                  = 2
  ram                    = 4096
  storage_size           = 50
  storage_type           = "SSD"
  location               = "de/fra"
  display_name           = "postgres-cluster"
  synchronization_mode   = "ASYNCHRONOUS"
  
  credentials {
    username = "postgres"
    password = "SuperSecurePassword123!"
  }

  connections {
    datacenter_id = ionos_datacenter.main.id
    lan_id        = ionos_lan.private.id
    cidr          = "10.0.0.0/24"
  }
}

output "web_server_ip" {
  value = ionos_server.web_server.primary_ip
}

output "total_monthly_cost_estimate" {
  value = "Run 'ionos-finops breakdown --path .' to calculate costs"
}
