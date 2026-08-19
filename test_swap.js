function swap(arr, index1, index2) {
    let temp = arr[index1];
    arr[index1] = arr[index2];
    arr[index2] = temp;
    console.log("Swapped " + arr[index1] + " and " + arr[index2]);
}
