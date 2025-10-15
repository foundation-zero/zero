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
pnpm run extract-schema-values THRUSTERS_PARAMETER_DEFINITION ThrustersParameterValuesType

# Custom extraction
pnpm run extract-schema-values <CONST_NAME> <TYPE_NAME>
```

**What it does:**
1. Parses the GraphQL schema file at `src/graphql/thrs/schema.graphql`
2. Finds the specified GraphQL type definition
3. Extracts field metadata from `@jsonSchemaDirective` annotations
4. Infers component types (control/sensor/parameter) from field metadata
5. Generates appropriate TypeScript definition objects with proper typing
6. Updates or creates the specified constant in `src/lib/consts.generated.ts`

### `generate-graphql-queries.js`

Generates GraphQL query fragments based on component type field mappings defined in `CONTROL_FIELDS` and `SENSOR_FIELDS`.

**Usage:**
```bash
# Generate control query
pnpm run generate-query THRUSTERS_CONTROL_QUERY ThrustersControlValuesType

# Generate sensor query  
pnpm run generate-query THRUSTERS_SENSOR_QUERY ThrustersSensorValuesType

# Generate parameter query
pnpm run generate-query THRUSTERS_PARAMETERS_QUERY ThrustersParameterValuesType

# Custom query generation
pnpm run generate-query <QUERY_NAME> <TYPE_NAME>
```

**What it does:**
1. Reads component definitions from `src/lib/consts.generated.ts`
2. Reads field mappings from `src/lib/consts.ts` (`CONTROL_FIELDS`, `SENSOR_FIELDS`)
3. Maps each component to its appropriate fields based on component type
4. Generates GraphQL query fragments with `{ value timestamp }` structure
5. Updates or creates the specified query constant in `src/lib/queries.generated.ts`

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
```

## Type System Integration

The generated definitions integrate with the TypeScript type system defined in `src/@types/thrs.ts`:

### Component Types

- **Controls**: `PumpControl`, `ValveControl` with fields like `dutypoint`, `on`, `setpoint`
- **Sensors**: `PumpSensor`, `TemperatureSensor`, `FlowSensor`, etc. with fields like `flow`, `speed`, `temperature`
- **Parameters**: Simple `number` or `PID` (tuple of 3 numbers) values for configuration

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

### npm Scripts
The following scripts are available in `package.json`:
- `extract-schema-values`: Runs the schema extraction script
- `generate-query`: Runs the GraphQL query generation script

## Error Handling

The scripts include comprehensive error handling:
- Validates that schema and constants files exist
- Checks that the target GraphQL type is found
- Provides clear error messages for debugging
- Exits with appropriate error codes for CI/CD integration
- Validates component type mappings and field definitions