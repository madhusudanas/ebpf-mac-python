package main

import "fmt"

func add(x int, y int) int {
  return x + y;
}

func main() {
  //var a int
  //var b int
  //fmt.Println("Enter a and b")
  //fmt.Scan(&a)
  //fmt.Scan(&b)
  fmt.Println("sum:", add(2, 3))
}
