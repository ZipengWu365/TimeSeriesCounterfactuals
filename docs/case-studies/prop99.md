# Case study: California Proposition 99

## Why this case matters

Prop99 is often the first policy example people encounter when learning synthetic control. It is intuitive, policy-relevant, and easy to explain in a classroom or lab meeting.

## Study defaults in `tscfbench`

- dataset id: `california_prop99`
- treated unit: `California`
- intervention year: `1989`
- outcome: `cigsale`

## Suggested command

```bash
python -m tscfbench make-canonical-spec --study-ids prop99 --data-source snapshot --no-external -o prop99.json
python -m tscfbench run-canonical prop99.json -o prop99_results.json
```

## Teaching tip

Use Prop99 to introduce space placebos before moving on to more technically involved inference add-ons.
