# Schema Extraction Scripts

This directory contains Node.js scripts for automatically extracting GraphQL schema definitions and generating TypeScript constants and GraphQL queries.

## Scripts

### `extract-schema-values.js`

Extracts fields from GraphQL schema types and generates TypeScript definition objects. Supports control, sensor, and parameter definitions with automatic type inference.

**Usage:**

```bash
# Extract control definitions
pnpm run extract-schema-values THRUSTERS_CONTROL_DEFINITION ThrustersControlValuesType

# Extract sensor definitions
pnpm run extract-schema-values THRUSTERS_SENSOR_DEFINITION ThrustersSensorValuesType

# Extract parameter definitions
pnpm run extract-schema-values THRUSTERS_PARAMETER_DEFINITION ThrustersParametersType

# Extract simulation input definitions
pnpm run extract-schema-values THRUSTERS_SIMULATION_INPUTS ThrustersSimulationInputsType

# Extract simulation output definitions
pnpm run extract-schema-values THRUSTERS_SIMULATION_OUTPUTS ThrustersSimulationOutputsType

# Custom extraction
pnpm run extract-schema-values <CONST_NAME> <TYPE_NAME>
```

**What it does:**

1. Parses the GraphQL schema file at `src/graphql/thrs/schema.graphql`
2. Finds the specified GraphQL type definition
3. Extracts field metadata from `@jsonSchemaDirective` annotations (for controls/sensors) or infers types directly (for parameters/simulation)
4. Infers component types (control/sensor/parameter/simulation) from field metadata and GraphQL types
5. Generates appropriate TypeScript definition objects with proper typing
6. Updates or creates the specified constant in `src/lib/consts.generated.ts`

### `generate-graphql-queries.js`

Generates GraphQL query fragments based on component type field mappings.

**Usage:**

```bash
# Generate control query
pnpm generate-graphql-queries THRUSTERS_CONTROL_DEFINITION THRUSTERS_CONTROL_QUERY

# Generate sensor query
pnpm generate-graphql-queries THRUSTERS_SENSOR_DEFINITION THRUSTERS_SENSOR_QUERY

# Generate parameter query
pnpm generate-graphql-queries THRUSTERS_PARAMETER_DEFINITION THRUSTERS_PARAMETERS_QUERY

# Generate simulation inputs query
pnpm generate-graphql-queries THRUSTERS_SIMULATION_INPUTS THRUSTERS_SIMULATION_INPUTS_QUERY

# Generate simulation outputs query
pnpm generate-graphql-queries THRUSTERS_SIMULATION_OUTPUTS THRUSTERS_SIMULATION_OUTPUTS_QUERY

# Generic usage for any module
pnpm generate-graphql-queries <INPUT_CONST_NAME> <OUTPUT_QUERY_NAME>
```

### `extract-all-schemas.sh`

Batch script that extracts all schema values and generates GraphQL queries for all modules (THRUSTERS, PVT, PCM, CONSUMERS) and their definition types (control, sensor, parameter, simulation inputs/outputs) in a single command.

**Usage:**

```bash
# Run all schema extractions and query generations at once
./scripts/extract-all-schemas.sh
```

**What it does:**

1. Executes all 20 `extract-schema-values` commands for all modules and definition types
2. Executes all 20 `generate-graphql-queries` commands for all modules and definition types
3. Processes all modules: THRUSTERS, PVT, PCM, CONSUMERS
4. Extracts all definition types: control, sensor, parameter, simulation inputs, simulation outputs
5. Updates `src/lib/consts.generated.ts` with all extracted definitions
6. Updates `src/lib/queries.generated.ts` with all generated GraphQL queries

**Total operations:** 40 commands (20 extractions + 20 query generations)

**Useful when:**

- GraphQL schema has been updated
- Need to regenerate all definitions and queries after schema changes
- Setting up the project from scratch
- Ensuring all modules are up to date
- Want to regenerate both TypeScript definitions and GraphQL queries in one go

## Generated Output

The scripts generate constants in `src/lib/consts.generated.ts` and `src/lib/queries.generated.ts`:

### Control Definitions

```typescript
export const THRUSTERS_CONTROL_DEFINITION = toControlDefinition({
  thrustersPump1: {
    yardTag: "50001194",
    componentType: ControlComponentType.Pump,
  },
  thrustersMixRecovery: {
    yardTag: "50001074",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  // ... more entries
});
```

**Control components** are identified by:

- `componentType`: `ControlComponentType.Pump` or `ControlComponentType.Valve`
- `valveType`: Additional valve classification for valve components
- `yardTag`: Physical system identifier

### Sensor Definitions

```typescript
export const THRUSTERS_SENSOR_DEFINITION = toSensorDefinition({
  thrustersPump1: {
    yardTag: "50001194",
    componentType: SensorComponentType.Pump,
  },
  thrustersTemperatureSupply: {
    yardTag: "50001038-28",
    componentType: SensorComponentType.Temperature,
  },
  // ... more entries
});
```

**Sensor components** are identified by:

- `componentType`: One of `SensorComponentType` enum values (Temperature, Pressure, Flow, Pump, Valve, Thruster, Pcs)
- `valveType`: Additional valve classification for valve sensors
- `yardTag`: Physical system identifier

### Parameter Definitions

```typescript
export const THRUSTERS_PARAMETER_DEFINITION = toParameterDefinition({
  maximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
  coolingTemperature: {
    componentType: ParametersType.Temperature,
  },
  coolingFlow: {
    componentType: ParametersType.Flow,
  },
  // ... more entries
});
```

**Parameter components** are identified by:

- `componentType`: One of `ParametersType` enum values (Temperature, Flow, Tuning)
- No `yardTag` required - parameters are configuration values, not physical components

### Simulation Definitions

```typescript
export const THRUSTERS_SIMULATION_INPUTS = toSimulationDefinition({
  thrustersAft: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  // ... more entries
});

export const THRUSTERS_SIMULATION_OUTPUTS = toSimulationDefinition({
  thrustersSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  thrustersModuleSupply: {
    componentType: SimulationComponentType.Flow,
  },
  // ... more entries
});
```

**Simulation components** are identified by:

- `componentType`: One of `SimulationComponentType` enum values (Thruster, Boundary, Temperature, Flow, Pcs)
- No `yardTag` required - simulation components are virtual system boundaries and inputs/outputs
- Automatically inferred from GraphQL field types (`ThrusterSimulationType`, `BoundarySimulationType`, etc.)

### Generated GraphQL Queries

```typescript
export const THRUSTERS_CONTROL_QUERY = `
  thrustersPump1 {
      dutypoint { value timestamp }
      on { value timestamp }
      }
  thrustersMixRecovery {
      setpoint { value timestamp }
      }
`;

export const THRUSTERS_SENSOR_QUERY = `
  thrustersPump1 {
      flow { value timestamp }
      speed { value timestamp }
      opTime { value timestamp }
      }
  thrustersTemperatureSupply {
      temperature { value timestamp }
      }
`;

export const THRUSTERS_SIMULATION_INPUTS_QUERY = `
    thrustersAft {
    heatFlow { value timestamp }
    active { value timestamp }
    }
    thrustersFwd {
    heatFlow { value timestamp }
    active { value timestamp }
    }
    thrustersSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
    }
    thrustersModuleSupply {
    temperature { value timestamp }
    }
    thrustersPcs {
    mode { value timestamp }
    }
`;

export const THRUSTERS_SIMULATION_OUTPUTS_QUERY = `
    thrustersSeawaterReturn {
    temperature { value timestamp }
    }
    thrustersModuleSupply {
    flow { value timestamp }
    }
    thrustersModuleReturn {
    temperature { value timestamp }
    flow { value timestamp }
    }
`;
```

## Type System Integration

The generated definitions integrate with the TypeScript type system defined in `src/@types/thrs.ts`:

### Component Types

- **Controls**: `PumpControl`, `ValveControl` with fields like `dutypoint`, `on`, `setpoint`
- **Sensors**: `PumpSensor`, `TemperatureSensor`, `FlowSensor`, etc. with fields like `flow`, `speed`, `temperature`
- **Parameters**: Simple `number` or `PID` (tuple of 3 numbers) values for configuration
- **Simulation**: `ThrusterSimulation`, `BoundarySimulation`, `TemperatureSimulation`, etc. with fields like `heatFlow`, `active`, `temperature`, `flow`

### Field Mappings

The `CONTROL_FIELDS` and `SENSOR_FIELDS` constants define which fields are included in queries:

```typescript
export const CONTROL_FIELDS: ControlFields = {
  [ControlComponentType.Pump]: ["dutypoint", "on"],
  [ControlComponentType.Valve]: ["setpoint"],
};

export const SENSOR_FIELDS: SensorFields = {
  [SensorComponentType.Pump]: ["flow", "speed", "opTime"],
  [SensorComponentType.Temperature]: ["temperature"],
  [SensorComponentType.Flow]: ["flow", "temperature"],
  // ... more mappings
};
```

## Integration with Development Workflow

### pnpm scripts

The following scripts are available in `package.json`:

- `extract-schema-values`: Runs the schema extraction script with arguments
- `generate-graphql-queries`: Runs the query generation script with arguments

**Examples:**

```bash
# Extract all definition types
pnpm extract-schema-values THRUSTERS_CONTROL_DEFINITION ThrustersControlValuesType
pnpm extract-schema-values THRUSTERS_SENSOR_DEFINITION ThrustersSensorValuesType
pnpm extract-schema-values THRUSTERS_PARAMETER_DEFINITION ThrustersParameterValuesType
pnpm extract-schema-values THRUSTERS_SIMULATION_INPUTS ThrustersSimulationInputsType
pnpm extract-schema-values THRUSTERS_SIMULATION_OUTPUTS ThrustersSimulationOutputsType

# Generate queries
pnpm generate-graphql-queries THRUSTERS_CONTROL_DEFINITION THRUSTERS_CONTROL_QUERY
pnpm generate-graphql-queries THRUSTERS_SENSOR_DEFINITION THRUSTERS_SENSOR_QUERY
pnpm generate-graphql-queries THRUSTERS_PARAMETER_DEFINITION THRUSTERS_PARAMETERS_QUERY
pnpm generate-graphql-queries THRUSTERS_SIMULATION_INPUTS THRUSTERS_SIMULATION_INPUTS_QUERY
pnpm generate-graphql-queries THRUSTERS_SIMULATION_OUTPUTS THRUSTERS_SIMULATION_OUTPUTS_QUERY
```

## Error Handling

The scripts include comprehensive error handling:

- Validates that schema and constants files exist
- Checks that the target GraphQL type is found
- Provides clear error messages for debugging
- Exits with appropriate error codes for CI/CD integration
- Validates component type mappings and field definitions
