# Test from Google VM

```bash
% gcloud run services describe ls-gunicorn-noslices --region=us-central1
✔ Service ls-gunicorn-noslices in region us-central1

URL:     https://ls-gunicorn-noslices-898747337195.us-central1.run.app
Ingress: all
Traffic:
  100% ls-gunicorn-noslices-00014-d4k
  0%   ls-gunicorn-noslices-00017-gd5
         bad: https://bad---ls-gunicorn-noslices-4hv6fcqvzq-uc.a.run.app

Service-level Min Instances: 60000

Last updated on 2024-11-21T11:36:28.929677Z by chen.xu@aalto.fi:
  Revision ls-gunicorn-noslices-00018-q2k
  Container None
    Image:           gcr.io/savvy-hybrid-329618/ls_gunicorn
    Port:            8080
    Memory:          1G
    CPU:             1000m
    Env vars:
      NO_SLICES      True
    Startup Probe:
      TCP every 240s
      Port:          8080
      Initial delay: 0s
      Timeout:       240s
      Failure threshold: 1
      Type:          Default
  Service account:   898747337195-compute@developer.gserviceaccount.com
  Concurrency:       1000
  Max Instances:     60000
  Timeout:           300s
```

Results

```bash
cxu@load-testing-vm:~/ls-gcp$ echo "POST $URL/process" | vegeta attack -duration=2s -rate=5000   -body=body.txt   -header "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"   -header "Authorization: Bearer $TOKEN" | vegeta report
Requests      [total, rate, throughput]         9999, 4993.76, 4658.40
Duration      [total, attack, wait]             2.146s, 2.002s, 143.504ms
Latencies     [min, mean, 50, 90, 95, 99, max]  609.658µs, 117.215ms, 90.958ms, 223.223ms, 277.764ms, 333.633ms, 1.378s
Bytes In      [total, mean]                     219912, 21.99
Bytes Out     [total, mean]                     4868052, 486.85
Success       [ratio]                           99.97%
Status Codes  [code:count]                      0:3  200:9996
```
