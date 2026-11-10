# Workflow agents: how the agents communicate

The movie-pitch system in [agent.py](agent.py) nests three kinds of workflow agent under one root agent. The agents never call each other directly. Control passes through the workflow structure (transfer, sequence, loop, parallel), and data passes through **session state**: each agent writes to state keys, and later agents read them in their instructions through `{ KEY? }` templates.

## Control flow

```mermaid
flowchart TD
    user(["User"])
    greeter["greeter<br/>(root Agent)"]

    user -->|"names a historical figure"| greeter
    greeter -->|"transfer to sub-agent"| fct

    subgraph fct["film_concept_team (SequentialAgent)"]
        direction TB

        subgraph wr["1. writers_room (LoopAgent, max_iterations=5)"]
            direction TB
            researcher["researcher<br/>tool: Wikipedia"]
            screenwriter["screenwriter"]
            critic["critic"]
            researcher --> screenwriter --> critic
            critic -->|"needs work:<br/>next iteration"| researcher
        end

        subgraph pt["2. preproduction_team (ParallelAgent)"]
            direction LR
            box["box_office_researcher"]
            casting["casting_agent"]
        end

        fw["3. file_writer<br/>tool: write_file"]

        critic -->|"good enough: exit_loop<br/>(or 5 iterations reached)"| pt
        pt -->|"both finished"| fw
    end

    fw --> out[/"movie_pitches/&lt;title&gt;.txt"/]
```

## Data flow through session state

Solid arrows are writes and dashed arrows are reads. The `append_to_state` tool appends to a list, so `research`, `PLOT_OUTLINE` and `CRITICAL_FEEDBACK` grow with each loop iteration. The parallel agents write a single value with `output_key`.

```mermaid
flowchart LR
    greeter["greeter"]
    researcher["researcher"]
    screenwriter["screenwriter"]
    critic["critic"]
    box["box_office_researcher"]
    casting["casting_agent"]
    fw["file_writer"]

    subgraph state["Session state"]
        direction TB
        PROMPT[("PROMPT")]
        research[("research")]
        PLOT[("PLOT_OUTLINE")]
        FEEDBACK[("CRITICAL_FEEDBACK")]
        BOR[("box_office_report")]
        CR[("casting_report")]
    end

    greeter -->|"append_to_state"| PROMPT
    researcher -->|"append_to_state"| research
    screenwriter -->|"append_to_state"| PLOT
    critic -->|"append_to_state"| FEEDBACK
    box -->|"output_key"| BOR
    casting -->|"output_key"| CR

    PROMPT -.-> researcher
    PLOT -.-> researcher
    FEEDBACK -.-> researcher

    PROMPT -.-> screenwriter
    PLOT -.-> screenwriter
    research -.-> screenwriter
    FEEDBACK -.-> screenwriter

    PLOT -.-> critic
    research -.-> critic

    PLOT -.-> box
    PLOT -.-> casting

    PLOT -.-> fw
    BOR -.-> fw
    CR -.-> fw
```

## Summary

| Agent | Type | Reads from state | Writes to state | Tools |
|---|---|---|---|---|
| `greeter` | `Agent` (root) | none | `PROMPT` | `append_to_state` |
| `film_concept_team` | `SequentialAgent` | none | none | none |
| `writers_room` | `LoopAgent` | none | none | none |
| `researcher` | `Agent` | `PROMPT`, `PLOT_OUTLINE`, `CRITICAL_FEEDBACK` | `research` | Wikipedia, `append_to_state` |
| `screenwriter` | `Agent` | `PROMPT`, `PLOT_OUTLINE`, `research`, `CRITICAL_FEEDBACK` | `PLOT_OUTLINE` | `append_to_state` |
| `critic` | `Agent` | `PLOT_OUTLINE`, `research` | `CRITICAL_FEEDBACK` | `append_to_state`, `exit_loop` |
| `preproduction_team` | `ParallelAgent` | none | none | none |
| `box_office_researcher` | `Agent` | `PLOT_OUTLINE` | `box_office_report` | none |
| `casting_agent` | `Agent` | `PLOT_OUTLINE` | `casting_report` | none |
| `file_writer` | `Agent` | `PLOT_OUTLINE`, `box_office_report`, `casting_report` | none (writes a file) | `write_file` |
