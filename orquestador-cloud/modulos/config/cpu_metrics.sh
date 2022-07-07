# Script a usar en los workers del Linux Cluster para recaudar las metricas del % de uso del CPU
#
# Se recibe dos argumentos:
#   1) interval: intervalo de tiempo del segundos para tomar la medicion de muestras
#   2) filename: nombre del archivo donde se guardara las metricas
#
# Ejemplo: ./cpu_metrics.sh 300 worker1_cpu_metrics & disown
#
# Se tomo de base el codigo realizado por Paul Colby (http://colby.id.au)

interval=$1
filename=$2

TEMP_INPUT=$(echo /sys/class/hwmon/hwmon1/{temp1_input,temp2_input,temp3_input})
PREV_TOTAL=0
PREV_IDLE=0

while true; do
  # Get the total CPU statistics, discarding the 'cpu ' prefix.
  CPU=(`sed -n 's/^cpu\s//p' /proc/stat`)
  IDLE=${CPU[3]} # Just the idle CPU time.

  # Calculate the total CPU time.
  TOTAL=0
  for VALUE in "${CPU[@]}"; do
    let "TOTAL=$TOTAL+$VALUE"
  done

  # Calculate the CPU usage since we last checked.
  let "DIFF_IDLE=$IDLE-$PREV_IDLE"
  let "DIFF_TOTAL=$TOTAL-$PREV_TOTAL"
  let "DIFF_USAGE=(1000*($DIFF_TOTAL-$DIFF_IDLE)/$DIFF_TOTAL+5)/10"

  # Redirect CPU temperature and % of CPU usage to file.
  # echo "$(date '+%H:%M:%S'): ${DIFF_USAGE}%" >> cpu.txt
  # En porcentaje (%)
  echo "$(date '+%Y-%m-%d %H:%M:%S'),${DIFF_USAGE}" >> $2

  # Remember the total and idle CPU times for the next check.
  PREV_TOTAL="$TOTAL"
  PREV_IDLE="$IDLE"

  # Wait before checking again.
  # Cada 5 minutos
  sleep $1
done