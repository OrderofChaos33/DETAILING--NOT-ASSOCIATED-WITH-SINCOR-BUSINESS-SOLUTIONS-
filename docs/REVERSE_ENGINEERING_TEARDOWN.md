# Competitor Teardown — Clean-Room Feature Mapping (2026-11-04)

Method: public marketing pages, pricing listings, and feature comparisons only.
No proprietary code, no login-gated scraping, no copying of copy or workflows
verbatim. We mapped *what capability is being sold* and rebuilt it in our own
code. Claims below are the advertisers' claims, not our results.

## The loud ads ("$70,000/month on autopilot", "never worry about leads again")

| Seller type seen in research | Headline claim | What is actually underneath |
|---|---|---|
| Agency growth systems (e.g. Elevate-style offers) | "$15K → $40K/mo in 90 days", "calendar fills itself" | Meta/Google ads + AI receptionist + automated SMS/email follow-up + a CRM pipeline. A 4-part system, sold to shops already doing $10K+/mo. |
| AI receptionists (e.g. Avoonta, ~$79/mo launch plan in its example) | "Calls quote requests in seconds", "books the job" | Form/ad triggers an outbound call in seconds, qualifies year/make/model + service, books into Google/HighLevel/Cal.com, discloses it is AI, respects 8am–8pm + do-not-call. |
| GoHighLevel agency snapshots ($997 installs seen) | "Answer every call, book every detail, win every review — on autopilot" | 12 prebuilt automations in GoHighLevel: AI caller/chatbot, missed-call text-back in <60s, DM automation, review harvesting, pipelines/tags, year-long nurture, A2P 10DLC setup. The "software" is mostly a configured snapshot of someone else's platform. |
| Korr-style installers | "Missed-call text-back paid for the system in 3 days" | Mobile-first website + missed-call text-back + online scheduling + 5-star review routing + reminders at 24h/2h. 7–10 day install. |

## The real detailing CRMs (the paywall worth studying)

| Product | Public pricing signals found | Detailing-specific capabilities that matter |
|---|---|---|
| Urable | ~$99/mo listings, 14-day trial | Online booking built for detailing, per-vehicle service history, scheduling to capacity, automated follow-ups that generate repeat jobs. |
| OrbisX | ~$100/mo in comparison tables | Feature breadth: VIN scanning, CARFAX integration, inventory/barcode, fleet tools, AI follow-ups. |
| Mobile Tech RX (now Urable lineage) | ~$99/mo + per-user signals | Vehicle-size pricing, packages/add-ons out of the box. |
| Detailer Flow | $97/mo listing | All-in-one for mobile detailers: smart booking page, payments/invoices, automated follow-ups, review requests, built-in website. "Live in 48h". |
| DetailerOS | $50/mo flat, whole team | AI photo quoting, auto-booking, deposit/invoice pay links, memberships, fleet, review requests at job completion, rebook prompts. "Leads → booked in under 60 seconds" is its loop slogan. |
| Jobber / Housecall Pro (generalists) | $199–349/mo class | Mature operations, but think in *properties/jobs*, not vehicles — need configuration for vehicle pricing, travel buffers, service radius, condition photos. |

## The pattern underneath every one of them

1. **Speed-to-lead < 60 seconds.** Missed-call text-back, instant form reply,
   or an AI call in seconds. This is the single highest-leverage piece;
   multiple sellers repeat the same stat in different words: the first
   shop to respond wins the job.
2. **Vehicle-first data.** Year/make/model, size class, paint/condition,
   photos, VIN, and *per-vehicle* service history — not a generic contact list.
3. **One pipeline.** Lead → qualified → booked → reminded → completed →
   reviewed → rebooked/reactivated. Tags and stages, owner alerts on hot leads.
4. **Reminders + no-show recovery.** Confirmation instant, reminders 24h and
   2h before, easy reschedule, win-back if they no-show.
5. **Review engine at completion.** Request fires the moment the job is done;
   happy → Google, unhappy → private channel + owner alert.
6. **Reactivation.** Maintenance nudges tied to the *service clock*:
   ~90 days after a detail, ~6 months after ceramic, seasonal
   decontamination after winter salt.
7. **Quote friction removed.** Package tiers by vehicle size, photo/condition
   intake so you price condition not just the car, clear included/excluded list.
8. **Compliance plumbing nobody advertises.** TCPA consent, STOP/opt-out,
   A2P 10DLC registration for US business texting, AI disclosure on AI calls,
   calling-hours windows. Skip this and the whole SMS engine gets filtered/blocked.

## What we deliberately did NOT copy from the ads

- **No deposit gate.** Several stacks use deposits to cut no-shows. The owner
  decided 2026-11-04: Clinton customers get a frictionless hold, backed by
  reminders + confirmation replies instead of an upfront charge.
- **No revenue promises.** "$70k/month" is an ad claim with no audited basis
  in the pages reviewed. This stack is a tool; results depend on lead flow,
  capacity (one bay is one bay), and showing up.
- **No fake AI receptionist claims.** Our SMS is real when Twilio is wired;
  until then the code honestly reports `sms_sent: false`.

## Where our build matches / exceeds / still lags

Matches: speed-to-lead webhook, missed-call text-back, vehicle-first schema,
size-based quoting, duration+buffer calendar, reminder/review/reactivation
logic, STOP handling, hardened production FastAPI config.
Exceeds the snapshot sellers: we own the code and data (no per-month platform
tribute, no snapshot lock-in), and pricing/calendar/nurture are unit-tested.
Still lags (see BUILD_ROADMAP): live Twilio A2P registration, Meta Lead Ads
app review/webhook verification, Google Calendar sync, photo intake, and an
AI voice receptionist are not built/live yet.
