{% if headscale_instances %}
[network]
%{ for instance in headscale_instances ~}
${instance.hostname} ansible_host=${instance.ip} ansible_user=${instance.user} ansible_become_pass='{{ host_passwords[inventory_hostname] }}'
%{ endfor ~}
{% endif %}
{% if c2_instances %}
[c2_segment]
%{ for instance in c2_instances ~}
${instance.hostname} ansible_host=${instance.ip} ansible_user=${instance.user} ansible_become_pass='{{ host_passwords[inventory_hostname] }}'
%{ endfor ~}
{% endif %}
{% if phish_instances %}
[phish_segment]
%{ for instance in phish_instances ~}
${instance.hostname} ansible_ssh_user=${instance.user} ansible_host=${instance.ip} 
%{ endfor ~}
{% endif %}