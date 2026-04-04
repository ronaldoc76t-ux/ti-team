# Discussion: Network Engineer ↔ SysAdmin

## Scénario 1: Server unreachable

**Network Engineer:**
Le serveur 10.20.30.45 est unreachable depuis ce matin. Je vérifie la connectivité?

**SysAdmin:**
Je check si le serveur est UP. Ping timeout.

**Network Engineer:**
Je vérifie le switch port. Gi1/0/25 montre "down/down". Câble problème?

**SysAdmin:**
Je physicallycheck. Ah, le câble network a été débranché lors du maintenance hier.

**Network Engineer:**
Je reconnecte le cable. Port should come up.

---

## Scénario 2: Port blocked par firewall

**SysAdmin:**
J'ai besoin d'accéder au port 8080 sur le serveur dev mais connection refused. Le service est UP.

**Network Engineer:**
Je check les rules firewall. Ah, rule manquante pour 8080. Je add:
```
iptables -A INPUT -p tcp --dport 8080 -s 10.0.0.0/8 -j ACCEPT
```

**SysAdmin:**
Merci. Je reteste.

---

## Scénario 3: DNS resolution failed

**SysAdmin:**
Plus de DNS sur les serveurs. Je peux pinger 8.8.8.8 mais pas résoudre les noms.

**Network Engineer:**
Tu utilises quel DNS server?

**SysAdmin:**
Le forwarder interne 10.1.1.53.

**Network Engineer:**
Je check. Le service unbound est down. Je restart.

**SysAdmin:**
Resolution works now. Thanks!