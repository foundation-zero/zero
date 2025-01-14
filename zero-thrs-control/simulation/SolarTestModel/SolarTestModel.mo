model SolarTestModel
  "Example showing use of the flat plate solar collector in a complete solar thermal system"
  extends Modelica.Icons.Example;
  replaceable package Medium = Buildings.Media.Water
    "Fluid in the storage tank";
  Buildings.Fluid.SolarCollectors.ASHRAE93  solCol(
    shaCoe=0,
    redeclare package Medium = Medium,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
    rho=0.2,
    nColType=Buildings.Fluid.SolarCollectors.Types.NumberSelection.Number,
    nPanels=5,
    sysConfig=Buildings.Fluid.SolarCollectors.Types.SystemConfiguration.Series,
    per=Buildings.Fluid.SolarCollectors.Data.GlazedFlatPlate.FP_SolahartKf(),
    nSeg=9,
    azi=0,
    til=0) "Flat plate solar collector model";
  Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(filNam=
    Modelica.Utilities.Files.loadResource("modelica://Buildings/Resources/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos"),
    computeWetBulbTemperature=false) "Weather data file reader";
  Buildings.Fluid.Sensors.TemperatureTwoPort TOut(
    T_start(displayUnit="K"),
    m_flow_nominal=solCol.m_flow_nominal,
    redeclare package Medium = Medium) "Temperature sensor";
  Buildings.Fluid.Sensors.TemperatureTwoPort TIn(m_flow_nominal=solCol.m_flow_nominal,
    redeclare package Medium = Medium) "Temperature sensor";
  Buildings.Fluid.Storage.Stratified tan(
    redeclare package Medium = Medium,
    hTan=1.8,
    VTan=1.5,
    dIns=0.07,
    m_flow_nominal=solCol.m_flow_nominal,
    nSeg=4)
    "Storage tank model";
  Buildings.HeatTransfer.Sources.FixedTemperature rooT(T=293.15)
    "Room temperature";
  Buildings.Fluid.Movers.Preconfigured.FlowControlled_dp pum(
    redeclare package Medium = Medium,
    m_flow_nominal = .04)
    "Pump forcing circulation through the system";
  Buildings.Fluid.Storage.ExpansionVessel exp(
    redeclare package Medium = Medium, V_start=0.1) "Expansion tank";
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor TTan
    "Temperature in the tank water";
  Buildings.Fluid.Sensors.MassFlowRate flowSensor(redeclare package Medium = Medium);
  Modelica.Blocks.Interfaces.RealInput pump_dp_in "Input Value for pump pressure";

equation 
  connect(solCol.port_b,TOut.port_a);
  connect(TIn.port_b,solCol.port_a);
  connect(weaDat.weaBus,solCol. weaBus);
  connect(rooT.port, tan.heaPorTop);
  connect(rooT.port, tan.heaPorSid);
  connect(pum.port_b, flowSensor.port_a);
  connect(flowSensor.port_b, TIn.port_a);
  connect(pum.port_a, exp.port_a);
  connect(exp.port_a, tan.port_b);
  connect(TOut.port_b, tan.port_a);
  connect(tan.heaPorVol[3], TTan.port);
  connect(pum.dp_in, pump_dp_in);
end SolarTestModel;