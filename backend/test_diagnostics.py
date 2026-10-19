from agents.diagnostics_agent import run_diagnostics

print("--- VPN ticket ---")
for line in run_diagnostics("VPN keeps disconnecting every few minutes"):
    print(line)

print("--- Coffee machine ticket ---")
print(run_diagnostics("The coffee machine on floor 2 is broken"))